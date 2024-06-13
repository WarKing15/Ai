import time

from autogpt_server.data import block, db, execution, graph
from autogpt_server.executor import ExecutionManager
from autogpt_server.server import AgentServer
from autogpt_server.util.service import PyroNameServer


def create_test_graph() -> graph.Graph:
    """
    ParrotBlock
                \
                 ---- TextCombinerBlock ---- PrintingBlock
                /
    ParrotBlock
    """
    nodes = [
        graph.Node(block_id=block.ParrotBlock.id),
        graph.Node(block_id=block.ParrotBlock.id),
        graph.Node(
            block_id=block.TextCombinerBlock.id,
            input_default={"format": "{text1},{text2}"},
        ),
        graph.Node(block_id=block.PrintingBlock.id),
    ]
    nodes[0].connect(nodes[2], "output", "text1")
    nodes[1].connect(nodes[2], "output", "text2")
    nodes[2].connect(nodes[3], "combined_text", "text")

    test_graph = graph.Graph(
        name="TestGraph",
        description="Test graph",
        nodes=nodes,
    )
    block.initialize_blocks()
    result = graph.create_graph(test_graph)

    # Assertions
    assert result.name == test_graph.name
    assert result.description == test_graph.description
    assert len(result.nodes) == len(test_graph.nodes)

    return result


def execute_agent(test_manager: ExecutionManager, test_graph: graph.Graph):
    # --- Test adding new executions --- #
    text = "Hello, World!"
    input_data = {"input": text}
    response = AgentServer.execute_agent(test_graph.id, input_data)
    executions = response["executions"]
    run_id = response["run_id"]
    assert len(executions) == 2

    def is_execution_completed():
        execs = AgentServer.get_executions(test_graph.id, run_id)
        return test_manager.queue.empty() and len(execs) == 4

    # Wait for the executions to complete
    for i in range(10):
        if is_execution_completed():
            break
        time.sleep(1)

    # Execution queue should be empty
    assert is_execution_completed()
    executions = AgentServer.get_executions(test_graph.id, run_id)

    # Executing ParrotBlock1
    exec = executions[0]
    assert exec.status == execution.ExecutionStatus.COMPLETED
    assert exec.run_id == run_id
    assert exec.output_name == "output"
    assert exec.output_data == "Hello, World!"
    assert exec.input_data == input_data
    assert exec.node_id == test_graph.nodes[0].id

    # Executing ParrotBlock2
    exec = executions[1]
    assert exec.status == execution.ExecutionStatus.COMPLETED
    assert exec.run_id == run_id
    assert exec.output_name == "output"
    assert exec.output_data == "Hello, World!"
    assert exec.input_data == input_data
    assert exec.node_id == test_graph.nodes[1].id

    # Executing TextCombinerBlock
    exec = executions[2]
    assert exec.status == execution.ExecutionStatus.COMPLETED
    assert exec.run_id == run_id
    assert exec.output_name == "combined_text"
    assert exec.output_data == "Hello, World!,Hello, World!"
    assert exec.input_data == {
        "format": "{text1},{text2}",
        "text1": "Hello, World!",
        "text2": "Hello, World!",
    }
    assert exec.node_id == test_graph.nodes[2].id

    # Executing PrintingBlock
    exec = executions[3]
    assert exec.status == execution.ExecutionStatus.COMPLETED
    assert exec.run_id == run_id
    assert exec.output_name == "status"
    assert exec.output_data == "printed"
    assert exec.input_data == {"text": "Hello, World!,Hello, World!"}
    assert exec.node_id == test_graph.nodes[3].id


def test_agent_execution():
    with PyroNameServer():
        time.sleep(0.3)
        db.connect()
        test_graph = create_test_graph()
        with ExecutionManager(1) as test_manager:
            execute_agent(test_manager, test_graph)
