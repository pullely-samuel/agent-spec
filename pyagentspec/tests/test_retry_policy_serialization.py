# Copyright © 2025 Oracle and/or its affiliates.
#
# This software is under the Apache License 2.0
# (LICENSE-APACHE or http://www.apache.org/licenses/LICENSE-2.0) or Universal Permissive License
# (UPL) 1.0 (LICENSE-UPL or https://oss.oracle.com/licenses/upl), at your option.

from pyagentspec import Agent, AgentSpecDeserializer, AgentSpecSerializer, RetryPolicy
from pyagentspec.flows.edges.controlflowedge import ControlFlowEdge
from pyagentspec.flows.flow import Flow
from pyagentspec.flows.nodes import ApiNode, EndNode, LlmNode, StartNode
from pyagentspec.llms import OciGenAiConfig
from pyagentspec.llms.ociclientconfig import OciClientConfigWithInstancePrincipal
from pyagentspec.property import Property
from pyagentspec.tools import RemoteTool
from pyagentspec.versioning import AgentSpecVersionEnum


def test_retry_policy_serialization_roundtrip_on_llm_config() -> None:
    retry_policy = RetryPolicy(max_attempts=3, request_timeout=0.5, initial_retry_delay=1)
    llm_config = OciGenAiConfig(
        name="oci",
        model_id="meta.llama-3.3-70b-instruct",
        compartment_id="ocid1.compartment.oc1..exampleuniqueID",
        client_config=OciClientConfigWithInstancePrincipal(
            name="oci-client",
            service_endpoint="https://example.invalid",
        ),
        retry_policy=retry_policy,
    )

    start = StartNode(
        name="start",
        inputs=[Property(json_schema={"title": "name", "type": "string"})],
    )
    node = LlmNode(
        name="node",
        llm_config=llm_config,
        prompt_template="Hi {{name}}!",
        inputs=[Property(json_schema={"title": "name", "type": "string"})],
    )
    end = EndNode(name="end")
    flow = Flow(
        name="f",
        start_node=start,
        nodes=[start, node, end],
        control_flow_connections=[
            ControlFlowEdge(name="start_to_node", from_node=start, to_node=node),
            ControlFlowEdge(name="node_to_end", from_node=node, to_node=end),
        ],
    )

    dumped = AgentSpecSerializer().to_dict(flow)
    loaded = AgentSpecDeserializer().from_dict(dumped)

    assert AgentSpecSerializer().to_dict(loaded) == dumped


def test_retry_policy_serialization_roundtrip_on_agent() -> None:
    retry_policy = RetryPolicy(max_attempts=3, request_timeout=0.5, initial_retry_delay=1)
    llm_config = OciGenAiConfig(
        name="oci",
        model_id="meta.llama-3.3-70b-instruct",
        compartment_id="ocid1.compartment.oc1..exampleuniqueID",
        client_config=OciClientConfigWithInstancePrincipal(
            name="oci-client",
            service_endpoint="https://example.invalid",
        ),
        retry_policy=retry_policy,
    )
    agent = Agent(name="a", system_prompt="hi", llm_config=llm_config)

    dumped = AgentSpecSerializer().to_dict(agent)
    loaded = AgentSpecDeserializer().from_dict(dumped)

    assert AgentSpecSerializer().to_dict(loaded) == dumped


def test_retry_policy_serialization_roundtrip_on_apinode_and_remotetool() -> None:
    retry_policy = RetryPolicy(max_attempts=3, request_timeout=0.5, initial_retry_delay=1)

    api_node = ApiNode(
        name="api",
        url="https://example.invalid",
        http_method="GET",
        retry_policy=retry_policy,
    )
    remote_tool = RemoteTool(
        name="rt",
        description="d",
        url="https://example.invalid",
        http_method="GET",
        retry_policy=retry_policy,
    )

    dumped_api = AgentSpecSerializer().to_dict(api_node)
    loaded_api = AgentSpecDeserializer().from_dict(dumped_api)
    assert AgentSpecSerializer().to_dict(loaded_api) == dumped_api

    dumped_tool = AgentSpecSerializer().to_dict(remote_tool)
    loaded_tool = AgentSpecDeserializer().from_dict(dumped_tool)
    assert AgentSpecSerializer().to_dict(loaded_tool) == dumped_tool


def test_retry_policy_present_in_current_version_serialization() -> None:
    retry_policy = RetryPolicy(max_attempts=3, request_timeout=0.5, initial_retry_delay=1)
    agent_with_retry = Agent(
        name="a",
        system_prompt="hi",
        llm_config=OciGenAiConfig(
            name="oci",
            model_id="meta.llama-3.3-70b-instruct",
            compartment_id="ocid1.compartment.oc1..exampleuniqueID",
            client_config=OciClientConfigWithInstancePrincipal(
                name="oci-client",
                service_endpoint="https://example.invalid",
            ),
            retry_policy=retry_policy,
        ),
    )

    dumped = AgentSpecSerializer().to_dict(
        agent_with_retry, agentspec_version=AgentSpecVersionEnum.current_version
    )

    dumped_llm_cfg = dumped["llm_config"]
    assert "retry_policy" in dumped_llm_cfg
