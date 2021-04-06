from typing import List, Optional

from pydantic import BaseModel


class f_cli_methods(BaseModel):
    name: str = ''


class f_cli_attribute_name(BaseModel):
    name: str = ''
    mandatory: bool = False
    description: str = ''
    default: bool = False
    url_suffix: bool = False
    show: bool = False
    delete: bool = False


class f_cli_command_attributes(BaseModel):
    name: str = ''
    description: str = ''
    url: str = ''
    attributes: Optional[List[f_cli_attribute_name]]
    use_put: bool = False
    show_only: bool = False
    no_show: bool = False
    update: bool = False
    delete: bool = False


class f_cli_command(BaseModel):
    command: f_cli_command_attributes


class f_cli(BaseModel):
    cli: List[f_cli_command]
