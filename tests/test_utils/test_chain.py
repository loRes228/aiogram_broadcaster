import re

import pytest

from aiogram_broadcaster.utils.chain import Chain


class MyChain(Chain["MyChain"], sub_name="chain"):
    pass


class MyRootChain(MyChain):
    __chain_root__ = True


class TestChainObject:
    def test_class_attrs(self):
        assert MyChain.__chain_entity__ is MyChain
        assert MyChain.__chain_sub_name__ == "chain"
        assert MyChain.__chain_root__ is False

        assert MyRootChain.__chain_entity__ is MyChain
        assert MyRootChain.__chain_sub_name__ == "chain"
        assert MyRootChain.__chain_root__ is True

    def test_init(self):
        chain = MyChain(name="test_name")
        assert chain.name == "test_name"
        assert chain.head is None
        assert chain.tail == []

    def test_name(self):
        chain = MyChain()
        assert id(chain) == int(chain.name, 16)

    def test_chain_bind(self):
        chain1 = MyChain()
        chain2 = MyChain()
        chain3 = MyChain()
        chain1.bind(chain2)
        chain2.bind(chain3)

        assert chain1.head is None
        assert chain1.tail == [chain2]
        assert tuple(chain1.chain_head) == (chain1,)
        assert tuple(chain1.chain_tail) == (chain1, chain2, chain3)

        assert chain2.head is chain1
        assert chain2.tail == [chain3]
        assert tuple(chain2.chain_head) == (chain2, chain1)
        assert tuple(chain2.chain_tail) == (chain2, chain3)

        assert chain3.head is chain2
        assert chain3.tail == []
        assert tuple(chain3.chain_head) == (chain3, chain2, chain1)
        assert tuple(chain3.chain_tail) == (chain3,)

    def test_parental_bind(self):
        parent = MyChain()
        child1 = MyChain()
        child2 = MyChain()
        parent.bind(child1, child2)

        assert parent.head is None
        assert parent.tail == [child1, child2]
        assert tuple(parent.chain_head) == (parent,)
        assert tuple(parent.chain_tail) == (parent, child1, child2)

        assert child1.head is parent
        assert child1.tail == []
        assert tuple(child1.chain_head) == (child1, parent)
        assert tuple(child1.chain_tail) == (child1,)

        assert child2.head is parent
        assert child2.tail == []
        assert tuple(child2.chain_head) == (child2, parent)
        assert tuple(child2.chain_tail) == (child2,)

    def test_repr_and_str(self) -> None:
        parent = MyChain(name="parent")
        child = MyChain(name="child")
        parent.bind(child)

        assert repr(parent) == "MyChain(name='parent', nested=[MyChain(name='child')])"
        assert repr(child) == "MyChain(name='child')"

        assert str(parent) == "MyChain(name='parent')"
        assert str(child) == "MyChain(name='child', parent=MyChain(name='parent'))"

    def test_one_fluent_bind(self):
        chain1 = MyChain()
        chain2 = MyChain()
        assert chain1.bind(chain2) == chain2

    def test_many_fluent_bind(self):
        chain1 = MyChain()
        chain2 = MyChain()
        chain3 = MyChain()
        assert chain1.bind(chain2, chain3) == chain1

    def test_bind_without_args(self):
        chain = MyChain()
        with pytest.raises(
            ValueError,
            match="At least one chain must be provided to bind.",
        ):
            chain.bind()

    def test_bind_invalid_type(self):
        chain = MyChain()
        with pytest.raises(
            TypeError,
            match="The chain must be an instance of MyChain, not a str.",
        ):
            chain.bind("invalid type")

    def test_bind_itself(self):
        chain = MyChain()
        with pytest.raises(
            ValueError,
            match="Cannot bind the chain on itself.",
        ):
            chain.bind(chain)

    def test_bind_already_bind(self):
        chain1 = MyChain(name="chain1")
        chain2 = MyChain(name="chain2")
        chain1.bind(chain2)
        with pytest.raises(
            RuntimeError,
            match=re.escape(
                "The MyChain(name='chain2') is already attached to MyChain(name='chain1').",
            ),
        ):
            chain1.bind(chain2)

    def test_circular_bind(self):
        chain1 = MyChain()
        chain2 = MyChain()
        chain1.bind(chain2)
        with pytest.raises(
            RuntimeError,
            match="Circular referencing detected.",
        ):
            chain2.bind(chain1)

    def test_bind_root(self):
        root_chain = MyRootChain(name="root_chain")
        chain = MyChain(name="chain")
        with pytest.raises(
            RuntimeError,
            match=re.escape(
                "MyRootChain(name='root_chain') cannot be attached to another chain.",
            ),
        ):
            chain.bind(root_chain)
