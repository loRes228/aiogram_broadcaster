import typing
from pathlib import Path

import aiogram

from .parser import parse_nodes
from .targets import TARGETS
from .template import INIT_TEMPLATE, TEMPLATE


CONTENTS_PATH = Path(__file__).parent.parent / "aiogram_broadcaster" / "contents"


def main() -> None:
    for target in TARGETS:
        content = TEMPLATE.render(
            nodes=list(parse_nodes(obj=target.method)),
            typing_all=typing.__all__,
            aiogram_types_all=aiogram.types.__all__,
            aiogram_methods_all=aiogram.methods.__all__,
            content_name=target.content_name,
            call_result=target.call_result,
            method_exec=target.method_exec,
            put_model_extra=target.put_model_extra,
            model_extra_nodes=target.model_extra_nodes,
        )
        content_file = CONTENTS_PATH / (target.content_file_name + ".py")
        content_file.write_text(data=content)
    content = INIT_TEMPLATE.render(targets=TARGETS)
    init_file = CONTENTS_PATH / "__init__.py"
    init_file.write_text(data=content)


if __name__ == "__main__":
    main()
