from pydantic import BaseModel

class StubNode(BaseModel):
    g_id: str    

    def exists(self,session):
        pass

    def create(self,session,G):
        pass

    def update(self,session,G):
        pass
    def delete(self,session,G):
        pass

class StubEdge(BaseModel):
    node_1_g_id: str
    node_2_g_id: str

    def exists(self,session):
        pass

    def create(self,session,G):
        pass

    def update(self,session,G):
        pass
    def delete(self,session,G):
        pass
