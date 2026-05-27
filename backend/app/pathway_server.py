import pathway as pw
from pipeline2 import Retriever

class InputSchema(pw.Schema):
    chat_id: int
    email: str
    queries: str
    # session_id: str = pw.column_definition(primary_key=True)

input_, output_writer = pw.io.http.rest_connector(
        webserver=pw.io.http.PathwayWebserver(host="0.0.0.0", port=8003),
        route="/ask",
        schema=InputSchema,
        delete_completed_queries=True
    )
input2 = input_.with_columns(user_id=pw.this.id)
retriever = Retriever()
output = retriever(input2)
input_.promise_universe_is_equal_to(output)
output = output.with_universe_of(input_)
# print(input_.typehints())
output_writer(output)
pw.run()