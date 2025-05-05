import sys
from typing import TextIO
from seedseeker.defs import IntegerRNG

class FileStreamGenerator(IntegerRNG):
    """
    Streams numbers from a filestream.
    """
    
    stream: TextIO
    path: str
    
    def __init__(self, path: str = "") -> None:
        """
        Attempts to read from file on `path` if provided, otherwise reads from `stdin`
        """
        
        self.path = path
        
        if path == "":
            self.stream = sys.stdin
        
        else:
            try:
                self.stream = open(path)
            
            except:
                sys.stderr.write(f"Error: File `{path}` does not exist or it is not accessible")
                sys.exit(2)
                
    def __next__(self):
        """
        
        """
        try:
                return int(self.stream.readline().strip())
            
        except:
            if self.path != "": self.stream.close()
            raise StopIteration