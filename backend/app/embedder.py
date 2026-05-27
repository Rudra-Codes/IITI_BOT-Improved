import pathway as pw
from sentence_transformers import SentenceTransformer
import numpy as np
# from pathway.xpacks.llm.splitters import RecursiveSplitter

PATH_INPUT = "data/data_collected.csv"
PATH_OUTPUT = "data/result.csv"

class IITIWebSchema(pw.Schema):
    row_id: str
    # url: str
    # title: str
    chunk: str
    # source_domain: str
    # metadata: str

init_table = pw.io.csv.read(
    PATH_INPUT,
    schema=IITIWebSchema,
    mode="streaming",
    # autocommit_duration_ms=1000
)

# Optionally check for non-empty body_text or metadata instead
final_table = init_table.filter(pw.this.chunk != "")
# pw.debug.compute_and_print(final_table)


# Load your model
model = SentenceTransformer("all-MiniLM-L6-v2")

# UDF to generate embeddings
@pw.udf
def batch_embedding(texts: str) -> list:
  # print(type(model.encode(texts)))
  return model.encode(texts)#.tolist()

# Add embeddings to each chunk
embedded = final_table.select(
    row_id=pw.this.row_id,
    chunk=pw.this.chunk,
    embedding=batch_embedding(pw.this.chunk),  # This batches internally
    # url=pw.this.url,
    # title=pw.this.title,
    # metadata=pw.this.metadata
)


pw.io.csv.write(
    table=embedded,
    filename= PATH_OUTPUT
)

pw.run()