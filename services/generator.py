import threading
from queue import Queue
from callbacks.stream import StreamingStdOutCallbackHandlerYield, generate
from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage, SystemMessage
from typing import List, Union, Callable

class Generator:
    def generate(self, messages: List[Union[HumanMessage, SystemMessage]], resolve_fn: Callable[[str], None]):               
        q = Queue()
        callback_fn = StreamingStdOutCallbackHandlerYield(q)
                
        def ask_question(callback_fn: StreamingStdOutCallbackHandlerYield, resolve_fn: Callable[[str], None]):
            chat_model = ChatOllama(
                model="llama2",
                callbacks=[callback_fn]
            )
            print("Asking question...")
            result = chat_model.invoke(messages)
            print("Question asked.")
            resolve_fn(str(result.content))
        
        threading.Thread(target=ask_question, args=(callback_fn, resolve_fn,)).start()
        
        return generate(q)
