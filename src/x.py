from pydantic import  BaseModel, BaseSettings, Field,root_validator
from abc import ABC, abstractmethod
from typing import Optional,Any,Dict,Type
from uuid import UUID
from discord import Attachment
from aiosupabase import Supabase, SupabaseAPI
import warnings




GENTLE_WARNING = (
    "You may be a victim of shitty open-source(langchain) "
    "try to use a clean and well designed API instead."
)

class Vectorizer(BaseModel):
    def create_vector(self,vec:"VecData"):
        ...
    


VectorManager = Vectorizer

class BaseMedia(BaseModel,ABC):
    id:Optional[UUID] = None
    file_name: Optional[str] = None
    vectors_ids: Optional[list] = None
    chunk_size: int = 500
    chunk_overlap: int = 20

    class Config:
        arbitrary_types_allowed = True


    @abstractmethod
    def gen_vectors(self,for_langchain=False):
        ...
    
    def compute_documents(self):
        warnings.warn(GENTLE_WARNING)
        return self.gen_vectors(for_langchain=True)



class FileLike(BaseMedia):
    file: Optional[Attachment] = None
    file_content: Optional[Any] = None
    file_extension: Optional[str] = None
    file_size: Optional[int] = None
    file_sha1: Optional[str] = None
    
    @property
    def content(self):
        return self.file_content

    @root_validator(pre=True)
    def _set_file_extension(cls,values:Dict):
        if not values.get("file_extension"):
            if not values.get("file"):
                values["file_extension"] = ""
            values["file_extension"] = values["file"].filename.split(".")[-1]
        return values

    def gen_vectors(self, for_langchain=False):
        ...
    
    
class Text(FileLike):
    ...

    
class LinkedContent(BaseMedia):
    ...

class Pdf(FileLike):
    ...


class Settings(BaseSettings):
    openai_api_key: str
    supabase_url: str
    supabase_client_key: str
    google_cloud_api_key: str
    discord_token: str
    apify_api_token: str
    
    class Config:
        env_file = ".env"



class VecData(BaseModel):
    '''Fuck you langchain you made dev experience like a shit'''
    
    content:str
    '''there's no such page_content stuff just content ok?'''

    meta_data:dict = Field(default_factory=dict)
    @property
    def page_content(self):
        warnings.warn(GENTLE_WARNING)
        return self.content
    
    @classmethod
    def create_from_pdf(cls):
        ...
    
    @classmethod
    def create_from_text(cls):
        ...
     
class DiscordVector(VecData):

    @classmethod
    def create_from_attchment(cls,attchment:Attachment):
        kls = create_file_loader(attchment.filename)
        kls().gen_vectors()
    
    @classmethod
    def create_from_msg(cls,msg:str):
        ...
       

Document = VecData



settings = Settings() # pyright:ignore
class FlexingFragments(BaseModel):

    supabase: SupabaseAPI
    
    @classmethod
    def create_reflex(cls):
        Supabase.configure(
            url=settings.supabase_url,
            key=settings.supabase_client_key
        )
        return cls(
            supabase=Supabase
        )

def create_file_loader(filename:str)->Type[BaseMedia]:
    match filename:
        case "md":
            ...
        case "txt":
            ...
        case "png","jpg","jpeg":
            ...
        case "pdf":
            return Pdf
        case _:
            ...
    
    return FileLike
    
