import uuid


class NotFoundRoleException(Exception):

    def __init__(self,
                 user_id: uuid.UUID,
                 dashboard_id: uuid.UUID
                 ):

        self.user_id = user_id
        self.dashboard_id = dashboard_id
        message = f"Not found role for user_id: {user_id} and dashboard_id: {dashboard_id}"

        self.message = message
        super().__init__(self.message)
