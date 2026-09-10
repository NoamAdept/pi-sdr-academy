from lib_flow import CopyBlock, Tag, TaggedSink, TaggedSource, run

SECRET = "offsets_are_metadata"
def transfer():
    source = TaggedSource([10, 20, 30, 40], [])
    sink = TaggedSink()
    # TODO: attach Tag(offset=2, key="secret", value=SECRET).
    # TODO: run through CopyBlock and post ("status", "done") as a message.
    return {"secret": "", "items": [], "messages": []}
