from enum import Enum
from typing import List


class IncorrectRoleException(Exception):

    def __init__(self,
                 required_roles: List[Enum],
                 actual_role: Enum
                 ):

        self.required_roles = required_roles
        self.actual_role = actual_role

        required_roles_str = ", ".join([role.value for role in self.required_roles])
        message = f"Incorrect role. Required roles: {required_roles_str} Actual: {self.actual_role}"

        self.message = message
        super().__init__(self.message)