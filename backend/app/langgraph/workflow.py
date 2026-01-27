from langgraph.graph import StateGraph, START, END

from app.langgraph.state import WorkflowState
from app.utils.read_pdf import read_pdf
from app.translator import translate_to_english

from app.components.fir_fact_extraction import extract_fir_fact
from app.components.ndps_legal_mapping import ndps_legal_mapping
from app.components.bns_legal_mapping import bns_legal_mapping
from app.components.bnss_legal_mapping import bnss_legal_mapping
from app.components.bsa_legal_mapping import bsa_legal_mapping
from app.components.investigation_plan import investigation_plan
from app.components.evidence_checklist import generate_evidence_checklist
from app.components.dos_and_dont import generate_dos_and_donts
from app.components.potential_prosecution_weaknesses import generate_potential_prosecution_weaknesses

# Create the workflow graph
workflow_graph = StateGraph(WorkflowState)

# Add all nodes to the graph
workflow_graph.add_node("read_pdf", read_pdf)
workflow_graph.add_node("translate_to_english", translate_to_english)
workflow_graph.add_node("extract_fir_fact", extract_fir_fact)
workflow_graph.add_node("ndps_legal_mapping", ndps_legal_mapping)
workflow_graph.add_node("bns_legal_mapping", bns_legal_mapping)
workflow_graph.add_node("bnss_legal_mapping", bnss_legal_mapping)
workflow_graph.add_node("bsa_legal_mapping", bsa_legal_mapping)
workflow_graph.add_node("investigation_plan", investigation_plan)
workflow_graph.add_node("generate_evidence_checklist", generate_evidence_checklist)
workflow_graph.add_node("generate_dos_and_donts", generate_dos_and_donts)
workflow_graph.add_node("generate_potential_prosecution_weaknesses", generate_potential_prosecution_weaknesses)

# Define the workflow edges
# Sequential: START -> read_pdf -> translate -> extract
workflow_graph.add_edge(START, "read_pdf")
workflow_graph.add_edge("read_pdf", "translate_to_english")
workflow_graph.add_edge("translate_to_english", "extract_fir_fact")

# Parallel: extract_fir_fact fans out to all 4 legal mapping nodes
workflow_graph.add_edge("extract_fir_fact", "ndps_legal_mapping")
workflow_graph.add_edge("extract_fir_fact", "bns_legal_mapping")
workflow_graph.add_edge("extract_fir_fact", "bnss_legal_mapping")
workflow_graph.add_edge("extract_fir_fact", "bsa_legal_mapping")

# Convergence: All 4 mapping nodes must complete before investigation_plan
workflow_graph.add_edge("ndps_legal_mapping", "investigation_plan")
workflow_graph.add_edge("bns_legal_mapping", "investigation_plan")
workflow_graph.add_edge("bnss_legal_mapping", "investigation_plan")
workflow_graph.add_edge("bsa_legal_mapping", "investigation_plan")

# Sequential: investigation_plan -> evidence_checklist
workflow_graph.add_edge("investigation_plan", "generate_evidence_checklist")

# Parallel: evidence_checklist fans out to dos_and_donts and prosecution_weaknesses
workflow_graph.add_edge("generate_evidence_checklist", "generate_dos_and_donts")
workflow_graph.add_edge("generate_evidence_checklist", "generate_potential_prosecution_weaknesses")

# Convergence: Both must complete before END
workflow_graph.add_edge("generate_dos_and_donts", END)
workflow_graph.add_edge("generate_potential_prosecution_weaknesses", END)

# Compile the graph (this is what gets invoked)
graph = workflow_graph.compile()

