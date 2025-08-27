import os
import re
from langchain_groq import ChatGroq
from youtube_transcript_api import YouTubeTranscriptApi #Importando a API de Transcrição do Youtube
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import WebBaseLoader
from langchain.prompts import ChatPromptTemplate #Invocando a função para criar templates no modelo

api_key_groq = "api_key" #Minha api key da groq

os.environ['GROQ_API_KEY'] = api_key_groq #Criando uma variável de ambiente pra armazenar minha api_key

chat = ChatGroq(model="deepseek-r1-distill-llama-70b") #Criando meu chat com o modelo DeepSeek R1

video_id = "4Yc06ndBsO8" 

try:
  dados_video_ufpa = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt','en'])
  print("Transcrição disponível:", dados_video_ufpa)
except Exception as e:
  print("Erro ao obter transcrição:", e)

loader = WebBaseLoader("https://lacis.ufpa.br")
#Criando uma variável que vai armazenas os scraps feitos pela função WebBaseLoader
#A função recebe como parâmetro o link da aplicação web

brutedata_lacis = loader.load()
#Descarregando os dados numa variável

dados_lacis = ""

for doc in brutedata_lacis:
  dados_lacis += doc.page_content

#Criando a lógica do chatbot
def resposta_bot(mensagens):

  #Criando mensagens de sistema para o chatbot lhe dando instruções
  mensagens_bot = [
    ('system', 'Você é um assistente virtual universitário chamado GuinAI'),
    ('system', 'Você tem acesso aos seguintes dados sobre o Lacis: {dados_informados}'),
    ('system', 'Você tem acesso aos seguintes dados sobre a Universidade Federal do Pará, a universidade sede do lacis: {dados_informados2}'),
  ] 
  
  mensagens_bot += mensagens #Somando a lista menssagens com respostas_bot, para o bot ter acesso a todas as mensagens da interção user-chat
  #Para o chat saber as mensagens enviadas pelo usuário e por ele mesmo.
  template = ChatPromptTemplate.from_messages(mensagens_bot) #Criando o template para o chat receber a instrução
  chain = template | chat #Criando minha cadeia de eventos
  return chain.invoke({'dados_informados': dados_lacis ,'dados_informados2': dados_video_ufpa}).content #Invocando o chat a partir da chain: template->invoke com a mensagem dada ao usuário salva na lista menssagens
  #As chaves representam que a mensagem vem da cadeia de eventos (template->mensagens_bot (onde todas as mensagens estão armazenadas)-> mensagem recebida do modelo)

#Uma chain, uma cadeia de processamentos. O primeiro processamento é feito e depois o segundo é feito
#Primeiro o template vai ser preenchido, logo depois ele é mandado ao chat

def remover_pensamento(resposta_cp):
  #Função caso use um modelo reasoning
  # Remove tudo entre <think> e </think> usando expressões regulares
  response_without_think = re.sub(r'<think>.*?</think>', '', resposta_cp, flags=re.DOTALL)
  return response_without_think.strip()

print("Bem-vindo ao GuinIA")

mensagens = [] #Lista que vai armazenar todas as perguntas e respostas da interação

while True:
  prompt = input("Usuário: ")
  if prompt.lower() == 'x':
    break
  mensagens.append(('user', prompt))
  resposta = resposta_bot(mensagens)
  mensagens.append(('assistant', resposta))
  print(f'GuinIA: {resposta}')

print("Muito obrigado por usar o GuinIA, volte sempre!")

