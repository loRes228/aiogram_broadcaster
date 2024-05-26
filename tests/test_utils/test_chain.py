import re

import pytest

from aiogram_broadcaster.utils.chain import ChainObject


class MyChainObject(ChainObject["MyChainObject"], sub_name="chain"):
    pass


class MyRootChainObject(MyChainObject):
    __chain_root__ = True


class TestChainObject:
    def test_class_attrs(self):
        assert MyChainObject.__chain_entity__ is MyChainObject
        assert MyChainObject.__chain_sub_name__ == "chain"
        assert MyChainObject.__chain_root__ is False

        assert MyRootChainObject.__chain_entity__ is MyChainObject
        assert MyRootChainObject.__chain_sub_name__ == "chain"
        assert MyRootChainObject.__chain_root__ is True

    def test_init(self):
        chain = MyChainObject(name="test_name")
        assert chain.name == "test_name"
        assert chain.head is None
        assert chain.tail == []

    def test_name(self):
        chain = MyChainObject()
        assert id(chain) == int(chain.name, 16)

    def test_chain_include(self):
        chain1 = MyChainObject()
        chain2 = MyChainObject()
        chain3 = MyChainObject()
        chain1.include(chain2)
        chain2.include(chain3)

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

    def test_parental_include(self):
        parent = MyChainObject()
        child1 = MyChainObject()
        child2 = MyChainObject()
        parent.include(child1, child2)

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
        parent = MyChainObject(name="parent")
        child = MyChainObject(name="child")
        parent.include(child)

        assert repr(parent) == "MyChainObject(name='parent', nested=[MyChainObject(name='child')])"
        assert repr(child) == "MyChainObject(name='child')"

        assert str(parent) == "MyChainObject(name='parent')"
        assert str(child) == "MyChainObject(name='child', parent=MyChainObject(name='parent'))"

    def test_valid_fluent_include(self):
        chain1 = MyChainObject()
        chain2 = MyChainObject()
        assert chain1.include(chain2) == chain2

    def test_invalid_fluent_include(self):
        chain1 = MyChainObject()
        chain2 = MyChainObject()
        chain3 = MyChainObject()
        assert chain1.include(chain2, chain3) is None

    def test_include_without_args(self):
        chain = MyChainObject()
        with pytest.raises(
            ValueError,
            match="At least one chain must be provided to include.",
        ):
            chain.include()

    def test_include_invalid_type(self):
        chain = MyChainObject()
        with pytest.raises(
            TypeError,
            match="The chain must be an instance of MyChainObject, not a str.",
        ):
            chain.include("invalid type")

    def test_include_itself(self):
        chain = MyChainObject()
        with pytest.raises(
            ValueError,
            match="Cannot include the chain on itself.",
        ):
            chain.include(chain)

    def test_include_already_included(self):
        chain1 = MyChainObject(name="chain1")
        chain2 = MyChainObject(name="chain2")
        chain1.include(chain2)
        with pytest.raises(
            RuntimeError,
            match=re.escape(
                "The MyChainObject(name='chain2') is already "
                "attached to MyChainObject(name='chain1').",
            ),
        ):
            chain1.include(chain2)

    def test_circular_include(self):
        chain1 = MyChainObject()
        chain2 = MyChainObject()
        chain1.include(chain2)
        with pytest.raises(
            RuntimeError,
            match="Circular referencing detected.",
        ):
            chain2.include(chain1)

    def test_include_root(self):
        root_chain = MyRootChainObject(name="root_chain")
        chain = MyChainObject(name="chain")
        with pytest.raises(
            RuntimeError,
            match=re.escape(
                "MyRootChainObject(name='root_chain') cannot be attached to another chain.",
            ),
        ):
            chain.include(root_chain)
