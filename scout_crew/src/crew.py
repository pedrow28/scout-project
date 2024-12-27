from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
#from langchain_community.utilities.sql_database import SQLDatabase
#from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from src.tools.sql_tools import SQLQueryTool, SQLQueryCheckerTool, SQLListTablesTool, SQLInfoTool
from langchain_openai import ChatOpenAI
from crewai_tools import FileReadTool
from crewai_tools import FileWriterTool
from dotenv import load_dotenv
import os

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

load_dotenv()
api_key = os.environ["OPENAI_API_KEY"]


# Tools
## SQL

sql_tools = [
	SQLQueryTool(),
	SQLQueryCheckerTool(),
	SQLListTablesTool(),
	SQLInfoTool()
	]


## Read files
file_read_tool = FileReadTool(file_path='data/stats.md')

## Write files
file_write_tool = FileWriterTool(file_path='output/report.md')

@CrewBase
class ScoutCrew():
	"""ScoutCrew crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def interpreter_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['interpreter_agent'],
			tools=[file_read_tool],
			verbose=True
		)

	@agent
	def analyst_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['analyst_agent'],
			tools=sql_tools,
			verbose=True
		)
	
	@agent
	def report_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['report_agent'],
			verbose=True
		)
	
	@agent
	def markdown_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['markdown_agent'],
			verbose=True
		)
	
	

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def requirement_analysis(self) -> Task:
		return Task(
			config=self.tasks_config['requirement_analysis'],
		)

	@task
	def data_analysis(self) -> Task:
		return Task(
			config=self.tasks_config['data_analysis'],
		)
	
	@task
	def report_generation(self) -> Task:
		return Task(
			config=self.tasks_config['report_generation'],
		)
	
	@task
	def markdown_generation(self) -> Task:
		return Task(
			config=self.tasks_config['markdown_generation'],
			output_file='report.md'
		)



	@crew
	def crew(self) -> Crew:
		"""Creates the ScoutCrew crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
