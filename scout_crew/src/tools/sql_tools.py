# Importações necessárias
from crewai.tools import BaseTool  # Classe base para definir ferramentas personalizadas
from pydantic import Field  # Gerenciamento de campos no modelo Pydantic
from langchain_community.utilities.sql_database import SQLDatabase  # Utilitário para conexões com bancos de dados SQL
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit  # Toolkit para interagir com SQL via agentes
from langchain_openai import ChatOpenAI  # Modelo de linguagem utilizado para processar queries SQL
from dotenv import load_dotenv
import os


load_dotenv()
api_key = os.environ["OPENAI_API_KEY"]

# Configuração inicial do banco de dados e ferramentas
# Conexão com o banco de dados usando SQLAlchemy e criação do toolkit
db = SQLDatabase.from_uri("sqlite:///data//statistics.db")  # Conexão com banco de dados SQLite
llm = ChatOpenAI(api_key=api_key, model_name="gpt-4o", temperature=0)  # Instância de LLM para auxiliar na interação
toolkit = SQLDatabaseToolkit(db=db, llm=llm)  # Toolkit para combinar LLM e SQL Database

# Ferramenta para execução de queries SQL
class SQLQueryTool(BaseTool):
    """
    Classe para executar queries SQL no banco de dados.
    """
    name: str = "SQL Query"  # Nome da ferramenta
    description: str = "Executes SQL queries in the database. Input should be a valid SQL query."  # Descrição da funcionalidade
    toolkit: SQLDatabaseToolkit = Field(default_factory=lambda: toolkit)  # Toolkit configurado com banco e LLM

    def _run(self, query: str) -> str:
        """
        Executa uma query SQL e retorna o resultado.
        """
        try:
            query_tool = self.toolkit.get_tools()[0]  # Recupera a ferramenta de execução de queries do toolkit
            return query_tool.run(query)  # Executa a query fornecida
        except Exception as e:
            return f"Query execution error: {str(e)}"  # Retorna o erro em caso de falha

# Ferramenta para obter informações sobre o esquema de tabelas
class SQLInfoTool(BaseTool):
    """
    Classe para recuperar informações sobre o esquema do banco de dados.
    """
    name: str = "SQL Schema Info"  # Nome da ferramenta
    description: str = "Retrieves schema information about database tables. Input should be table names."  # Descrição da funcionalidade
    toolkit: SQLDatabaseToolkit = Field(default_factory=lambda: toolkit)  # Toolkit configurado com banco e LLM

    def _run(self, tables: str) -> str:
        """
        Recupera informações sobre o esquema das tabelas especificadas.
        """
        try:
            info_tool = self.toolkit.get_tools()[1]  # Recupera a ferramenta de informações do esquema do toolkit
            return info_tool.run(tables)  # Executa a consulta para recuperar o esquema
        except Exception as e:
            return f"Schema info retrieval error: {str(e)}"  # Retorna o erro em caso de falha

# Ferramenta para listar todas as tabelas disponíveis
class SQLListTablesTool(BaseTool):
    """
    Classe para listar todas as tabelas disponíveis no banco de dados.
    """
    name: str = "SQL List Tables"  # Nome da ferramenta
    description: str = "Lists all available tables in the database. No input required."  # Descrição da funcionalidade
    toolkit: SQLDatabaseToolkit = Field(default_factory=lambda: toolkit)  # Toolkit configurado com banco e LLM

    def _run(self, tool_input: str = "") -> str:
        """
        Lista todas as tabelas no banco de dados.
        """
        try:
            list_tool = self.toolkit.get_tools()[2]  # Recupera a ferramenta de listagem de tabelas do toolkit
            return list_tool.run("")  # Executa a listagem de tabelas
        except Exception as e:
            return f"Table listing error: {str(e)}"  # Retorna o erro em caso de falha

# Ferramenta para validar queries SQL antes de execução
class SQLQueryCheckerTool(BaseTool):
    """
    Classe para validar queries SQL antes da execução.
    """
    name: str = "SQL Query Checker"  # Nome da ferramenta
    description: str = "Validates SQL query syntax before execution. Input should be a SQL query."  # Descrição da funcionalidade
    toolkit: SQLDatabaseToolkit = Field(default_factory=lambda: toolkit)  # Toolkit configurado com banco e LLM

    def _run(self, query: str) -> str:
        """
        Valida a sintaxe de uma query SQL.
        """
        try:
            checker_tool = self.toolkit.get_tools()[3]  # Recupera a ferramenta de validação de queries do toolkit
            return checker_tool.run(query)  # Executa a validação
        except Exception as e:
            return f"Query validation error: {str(e)}"  # Retorna o erro em caso de falha