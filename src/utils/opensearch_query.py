def build_search_query(query_embedding, top_k=100, size=10):
    return {
        "size": 0,
        "query": {"knn": {"embedding": {"vector": query_embedding, "k": top_k}}},
        "_source": {"excludes": ["embedding"]},
        "aggs": {
            "group_by_filename": {
                "terms": {"field": "filename", "size": size},
                "aggs": {
                    "top_hits_per_file": {
                        "top_hits": {
                            "size": 1,
                            "_source": {"includes": ["filename", "chunk", "_score"]},
                        }
                    },
                    "avg_score": {"avg": {"script": {"source": "_score"}}},
                    "max_score": {"max": {"script": {"source": "_score"}}},
                    "std_deviation_score": {
                        "extended_stats": {"script": {"source": "_score"}}
                    },
                    "bucket_sort": {
                        "bucket_sort": {
                            "sort": [{"avg_score": {"order": "desc"}}],
                            "size": size,
                        }
                    },
                },
            }
        },
    }


def build_search_query2(query_embedding, size):
    return {
        "size": size,
        "query": {"knn": {"embedding": {"vector": query_embedding, "k": size}}},
    }


def build_create_query():
    return {
        "settings": {"index": {"knn": True}},
        "mappings": {
            "properties": {
                "filename": {"type": "keyword"},
                "chunk": {"type": "text"},
                "embedding": {"type": "knn_vector", "dimension": 384},
            }
        },
    }


def build_create_query2():
    return {
        "settings": {"index": {"knn": True}},
        "mappings": {
            "properties": {
                "document": {"type": "text"},
                "embedding": {"type": "knn_vector", "dimension": 384},
            }
        },
    }


def build_index_query(filename, chunk, embedding):
    return {
        "filename": filename,
        "chunk": chunk,
        "embedding": embedding,
    }


def build_index_query2(doc_text, embedding):
    return {"document": doc_text, "embedding": embedding}
