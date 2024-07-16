def build_search_query(query_embedding, top_k=100, size=10):
    return {
        "size": 0,
        "query": {
            "knn": {
                "embedding": {
                    "vector": query_embedding,
                    "k": top_k
                }
            }
        },
        "_source": {
            "excludes": ["embedding"]
        },
        "aggs": {
            "group_by_filename": {
                "terms": {
                    "field": "filename",
                    "size": size
                },
                "aggs": {
                    "top_hits_per_file": {
                        "top_hits": {
                            "size": 1,
                            "_source": {
                                "includes": ["filename", "chunk", "_score"]
                            }
                        }
                    },
                    "avg_score": {
                        "avg": {
                            "script": {
                                "source": "_score"
                            }
                        }
                    },
                    "max_score": {
                        "max": {
                            "script": {
                                "source": "_score"
                            }
                        }
                    },
                    "std_deviation_score": {
                        "extended_stats": {
                            "script": {
                                "source": "_score"
                            }
                        }
                    },
                    "bucket_sort": {
                        "bucket_sort": {
                            "sort": [
                                {
                                    "avg_score": {
                                        "order": "desc"
                                    }
                                }
                            ],
                            "size": size
                        }
                    }
                }
            }
        }
    }
