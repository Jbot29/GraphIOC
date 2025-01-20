from pydantic import BaseModel

class BaseNode(BaseModel):
    g_id: str    

    def exists(self,session):
        pass

    def create(self,session,G):
        pass
    
    def read(self,session):
        pass

    def update(self,session,G):
        pass
    def delete(self,session,G):
        pass
    def diff(self,session,G,diff_object):
        pass

    def export(self):

        class_name = self.__class__.__name__
        # Build a comma-separated list of key=value pairs using repr(value)
        fields_str = ", ".join(
            f"{k}={repr(v)}"
            for k, v in self.dict().items()
        )
        # Construct something like: MyModel(field1='abc', field2=123)
        return f"{class_name}({fields_str})"    

class BaseEdge(BaseModel):
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
