from fastmcp import FastMCP
from dotenv import load_dotenv
from starlette.middleware import CORSMiddleware
from starlette.middleware import Middleware

load_dotenv()

mcp = FastMCP(name='Notes App') # MCP client and host will be able to see

@mcp.tool() #then define a function which defines the tool you want to make
def get_my_notes() -> str : # returns a string , making something that makes new notes and deletes them
    '''Get all notes for a user'''

    return 'no notes'
@mcp.tool()
def add_note(content: str ) -> str :
    '''Add a note for a user'''
    return f'added note: {content}'
# running server after tools have been made
if __name__ == '__main__':
    mcp.run(
        transport='http',
        host='127.0.0.1',# running this on local host
        port=8000, #
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=['*'],
                allow_credentials=True,
                allow_methods=['*'],
                allow_headers=['*'],
            )
        ] # allows you to connect to the server when your not the same local host domain
    ) # allowing anyone to c0nnect to mcp server and use it