import os
import yaml
import openai
from openai import AzureOpenAI
from streamlit_chat import message

class LOAD_CONFIG():
    def __init__(self,
                 config_file: str) -> None:
        ## Prepare config file
        self.config_file = config_file
        self.load_config()

        ## Configuration for Variables
        self.AOAI_client = None
        self.AZURE_ENDPOINT = self.config['AOAI']['ENDPOINT']
        self.AZURE_OPENAI_KEY = self.config['AOAI']['KEY']
        self.AZURE_OPENAI_VER = self.config['AOAI']['VERSION']

        ## PARAMETERS FOR AOAI MODEL
        self.AOAI_MODEL = self.config['AOAI']['MODEL']
        self.AOAI_TEMPERATURE = self.config['AOAI']['PARAMTERS']['TEMPERATURE']
        self.AOAI_MAX_TOKENS = self.config['AOAI']['PARAMTERS']['MAX_TOKENS']
        self.AOAI_TOP_P = self.config['AOAI']['PARAMTERS']['TOP_P']
        self.AOAI_FREQUENCY_PENALTY = self.config['AOAI']['PARAMTERS']['FREQUENCY_PENALTY']
        self.AOAI_PRESENCE_PENALTY = self.config['AOAI']['PARAMTERS']['PRESENCE_PENALTY']

    def load_config(self):
        '''
        Load and extract config yml file.
        '''
        try:
            ### The file encoding specification (utf-8) is for running on Windows OS.
            ### If not specified, the following error will occur.
            ### UnicodeDecodeError: 'cp932' codec can't decode byte...
            with open(self.config_file, encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
        except Exception as e:
            print(e)
            raise

class AOAI_TOOLS(LOAD_CONFIG):
    def __init__(self,
                 config_file: str) -> None:
        super().__init__(config_file)

        ## variables for prompts
        self.promptBank = dict()

    def load_prompts(self,
                     prompt_name: str,
                     prompt_path: str) -> list:
        '''
        Load prepared prompts in yml file
        '''
        try:
            ## Open specified prompts
            ### The file encoding specification (utf-8) is for running on Windows OS.
            ### If not specified, the following error will occur.
            ### UnicodeDecodeError: 'cp932' codec can't decode byte...
            with open(prompt_path, encoding='utf-8') as f:
                d = yaml.safe_load(f)
            ## store prompts
            self.promptBank[prompt_name] = d
        except Exception as e:
            print(e)
            raise

    def setClient(self):
        '''
        Configuration for client on Azure OpenAI
        '''
        try:
            ## Configuration
            self.AOAI_client = AzureOpenAI(
                azure_endpoint = self.AZURE_ENDPOINT, 
                api_key=self.AZURE_OPENAI_KEY,  
                api_version=self.AZURE_OPENAI_VER
            )
        except Exception as e:
            print(e)
            raise

    def send_message_to_openai(self,
                               message_text:str) -> str:
        try:
            return self.AOAI_client.chat.completions.create(
                                                    model=self.AOAI_MODEL, 
                                                    messages = message_text,
                                                    temperature=self.AOAI_TEMPERATURE,
                                                    max_tokens=self.AOAI_MAX_TOKENS,
                                                    top_p=self.AOAI_TOP_P,
                                                    frequency_penalty=self.AOAI_FREQUENCY_PENALTY,
                                                    presence_penalty=self.AOAI_PRESENCE_PENALTY,
                                                    stop=None
                                                    )
        except Exception as e:
            print(e)
            raise

    def setAOAIformat(self,
                      message:str,
                      role:str) -> dict:
        '''
        Convert message to dict
        '''
        try:
            tmp_prompt = dict()
            tmp_prompt['role'] = role
            tmp_prompt['content'] = message
            return tmp_prompt
        except Exception as e:
            print(e)
            raise

    def extractOutput(self,
                      output: openai.types.chat.chat_completion.ChatCompletion) -> str:
        ''' 
        extract returned message
        '''
        try:
            return output.choices[0].message.content
        except Exception as e:
            print(e)
            raise

    def generate_conversation(self,
                              conversation_number: int,
                              prompt_caller: str,
                              prompt_operator: str) -> None:
        '''
        Generate conversation with both prompts for caller and operator
        '''
        prompts_caller, prompts_operator = [], []
        output_operator = None
        Conversation = []

        ## Define initial prompt for caller as system message
        content_caller_for_caller = self.setAOAIformat(message=prompt_caller, role='system')
        ## Define initial prompt for operator as system message
        content_operator = self.setAOAIformat(message=prompt_operator, role='system')

        for _ in range(conversation_number):
            # Caller -> Operator
            ## Set a message for caller
            prompts_caller.append(content_caller_for_caller)
            ## Set 
            if output_operator is not None:
                content_operator = self.setAOAIformat(message=self.extractOutput(output_operator), role='assistant')
                content_operator_for_caller = self.setAOAIformat(message=self.extractOutput(output_operator), role='user')
                prompts_caller.append(content_operator_for_caller)
            ## a message from caller to operator
            output_caller = self.send_message_to_openai(message_text=prompts_caller)
            ## Store the conversation
            Conversation.append(self.extractOutput(output_caller))
            print(f'Caller: {self.extractOutput(output_caller)}')

            # Operator -> Caller
            ## Set message by caller
            content_caller = self.setAOAIformat(message=self.extractOutput(output_caller), role='user')
            content_caller_for_caller = self.setAOAIformat(message=self.extractOutput(output_caller), role='assistant')
            ## Set the message in the prompt
            prompts_operator.append(content_operator)
            prompts_operator.append(content_caller)
            ## a message from operator to caller
            output_operator = self.send_message_to_openai(message_text=prompts_operator)

            Conversation.append(self.extractOutput(output_operator))
            print(f'Operator: {self.extractOutput(output_operator)}')

    def generate_conversation_on_UI(self,
                                    prompt_caller: str,
                                    prompt_operator: str,
                                    conversation_number: int) -> None:

        ## Conversation
        prompts_caller, prompts_operator = [], []
        output_operator = None

        ## Define initial prompt for caller as system message
        content_caller_for_caller = self.setAOAIformat(message=prompt_caller, role='system')
        ## Define initial prompt for operator as system message
        content_operator = self.setAOAIformat(message=prompt_operator, role='system')

        for _ in range(conversation_number):
            # Caller -> Operator
            ## Set a message for caller
            prompts_caller.append(content_caller_for_caller)
            ## Set 
            if output_operator is not None:
                content_operator = self.setAOAIformat(message=self.extractOutput(output_operator), role='assistant')
                content_operator_for_caller = self.setAOAIformat(message=self.extractOutput(output_operator), role='user')
                prompts_caller.append(content_operator_for_caller)
            ## a message from caller to operator
            output_caller = self.send_message_to_openai(message_text=prompts_caller)
            message(self.extractOutput(output_caller), is_user=False)

            # Operator -> Caller
            ## Set message by caller
            content_caller = self.setAOAIformat(message=self.extractOutput(output_caller), role='user')
            content_caller_for_caller = self.setAOAIformat(message=self.extractOutput(output_caller), role='assistant')
            ## Set the message in the prompt
            prompts_operator.append(content_operator)
            prompts_operator.append(content_caller)
            ## a message from operator to caller
            output_operator = self.send_message_to_openai(message_text=prompts_operator)
            message(self.extractOutput(output_operator), is_user=True)


