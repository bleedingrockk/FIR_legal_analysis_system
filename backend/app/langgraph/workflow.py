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
from app.components.forensic_legal_mapping import forensic_legal_mapping

# create a graph
graph = StateGraph(WorkflowState)

# add nodes
graph.add_node("read_pdf", read_pdf)
graph.add_node("translate_to_english", translate_to_english)
graph.add_node("extract_fir_fact", extract_fir_fact)
graph.add_node("ndps_legal_mapping", ndps_legal_mapping)
graph.add_node("bns_legal_mapping", bns_legal_mapping)
graph.add_node("bnss_legal_mapping", bnss_legal_mapping)
graph.add_node("bsa_legal_mapping", bsa_legal_mapping)
graph.add_node("forensic_legal_mapping", forensic_legal_mapping)
graph.add_node("investigation_plan", investigation_plan)

# add edges
graph.add_edge(START, "read_pdf")
graph.add_edge("read_pdf", "translate_to_english")
graph.add_edge("translate_to_english", "extract_fir_fact")
graph.add_edge("extract_fir_fact", "forensic_legal_mapping")
graph.add_edge("forensic_legal_mapping", END)

# # All four legal mappings run in parallel from extract_fir_fact
# graph.add_edge("extract_fir_fact", "ndps_legal_mapping")
# graph.add_edge("extract_fir_fact", "bns_legal_mapping")
# graph.add_edge("extract_fir_fact", "bnss_legal_mapping")
# graph.add_edge("extract_fir_fact", "bsa_legal_mapping")

# # All four must complete before investigation_plan (LangGraph waits for all parallel paths)
# graph.add_edge("ndps_legal_mapping", "investigation_plan")
# graph.add_edge("bns_legal_mapping", "investigation_plan")
# graph.add_edge("bnss_legal_mapping", "investigation_plan")
# graph.add_edge("bsa_legal_mapping", "investigation_plan")

# # investigation_plan runs after all legal mappings complete
# graph.add_edge("investigation_plan", END)

# compile the graph
graph = graph.compile()

