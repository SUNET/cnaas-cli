import yaml

from typing import List, Optional
from pydantic import BaseModel, Schema


class f_cli_attribute_name(BaseModel):
    name: str = ''
    mandatory: bool = False
    description: str = ''


class f_cli_command_attributes(BaseModel):
    name: str = ''
    description: str = ''
    url: str = ''
    attributes: List[f_cli_attribute_name]


class f_cli_command(BaseModel):
    command: f_cli_command_attributes


class f_cli(BaseModel):
    cli: List[f_cli_command]
