from lib_flow import CopyBlock,Tag,TaggedSink,TaggedSource,run

SECRET = "offsets_are_metadata"

def transfer():
    source=TaggedSource([10,20,30,40],[Tag(2,"secret",SECRET)]); sink=TaggedSink()
    run(source,[CopyBlock()],sink); sink.post_message("status","done")
    value=next(t.value for t in sink.tags if t.key=="secret")
    return {"secret":value,"items":sink.items.tolist(),"messages":sink.messages}
