const express = require("express");
const { Client } = require("@elastic/elasticsearch");
const fs = require("fs");

const app = express();
app.use(express.json());
app.use(express.static('component'));

const PORT = 8000;

const gamesData = JSON.parse(fs.readFileSync("game.json", "utf8"));
const client = new Client({ node: 'http://localhost:9200' });

const indexName = 'games';

const startServer = async () => {
    try {
        const indexExists = await client.indices.exists({ index: indexName });
        if (!indexExists.body) {
            await client.indices.create({ index: indexName });
        }
        
        const body = gamesData.flatMap(doc => [{ index: { _index: indexName } }, doc]);
        const { body: bulkResponse } = await client.bulk({ refresh: true, body });

        if (bulkResponse.errors) {
            console.error("Failed to index some documents:", bulkResponse.items);
        } else {
            console.log("Successfully indexed documents.");
        }

        app.get('/search', async (req, res) => {
            const { q } = req.query;

            if (!q) {
                return res.status(400).send({ error: "Query parameter q is required." });
            }

            try {
                const result = await client.search({
                    index: indexName,
                    size: 100,
                    body: {
                        query: {
                            bool: {
                                should: [
                                    {
                                        multi_match: {
                                            query: q,
                                            fields: ['name_original'],
                                            boost: 5,
                                        },
                                    },
                                    {
                                        multi_match: {
                                            query: q,
                                            fields: ['genres.name'],
                                            boost: 3,
                                        },
                                    },
                                    {
                                        multi_match: {
                                            query: q,
                                            fields: ['tags.name'],
                                            boost: 1,
                                        },
                                    },
                                    {
                                        multi_match: {
                                            query: q,
                                            fields: ['description'],
                                        },
                                    },
                                    {
                                        multi_match: {
                                            query: q,
                                            fields: ['publishers.name']
                                        },
                                    },
                                    {
                                        multi_match: {
                                            query: q,
                                            fields: ['developers.name']
                                        },
                                    }
                                ],
                            },
                        },
                        collapse: {
                            field: 'name_original.keyword',
                        },
                    },
                });

                const hits = result.body.hits.hits.map(hit => hit._source);

                res.send({ results: hits });
            } catch (error) {
                console.error("Elasticsearch error:", error);
                res.status(500).send({ error: "Failed to search." });
            }
        });

        app.listen(PORT, () => {
            console.log(`Server started on http://localhost:${PORT}`);
        });
    } catch (error) {
        console.error("Error during startup:", error);
    }
};

startServer();
