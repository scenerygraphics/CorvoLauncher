import requests
import json
import asyncio
import aiohttp
import time


# index of all datasets and their collections: https://api.cellxgene.cziscience.com/dp/v1/datasets/index
# index of all collections with names and IDs: https://api.cellxgene.cziscience.com/dp/v1/collections/index
class CellxGeneJSONRequests:
    def __init__(self):
        self.collections_url = "https://api.cellxgene.cziscience.com/dp/v1/collections/"
        self.collections_json = requests.get(self.collections_url + "index").json()

        self.collections = {}
        for i in self.collections_json:
            self.collections[i["name"]] = i["id"]

        self.test_download()
        # return collection names: self.collections.keys()
        # return collection ids: self.collections.values()

        # extract all datasets and their names and ids
        # for key in self.collections.keys(): self.get_collection_datasets(self.collections[key])

        # async address fetching
        # websites = ["https://api.cellxgene.cziscience.com/dp/v1/collections/0a77d4c0-d5d0-40f0-aa1a-5e1429bcbd7e",
        #             "https://api.cellxgene.cziscience.com/dp/v1/collections/"]
        # start = time.time()
        # asyncio.run(self.main_concurrent(websites))
        # end = time.time()
        # print("Took {} seconds.".format(end - start))

    def test_download(self):
        # example call sequence to download a dataset within a collection by name
        t_sapient_collect = self.get_collection_datasets(
            self.collections["A transcriptional cross species map of pancreatic islet cells"])
        self.download_dataset(t_sapient_collect, "mouse pancreatic islet cells")


    def get_collection_datasets(self, collection_id: str):
        dset_map = {}
        for i in requests.get(self.collections_url + collection_id).json()["datasets"]:
            # index 0 for .h5ad files
            # id determines filetype downloaded, dataset_id determines dataset within collection
            dset_map[i["name"]] = {"dataset_id": i["dataset_assets"][0]["dataset_id"],
                                   "filetype_id": i["dataset_assets"][0]["id"]}
        return dset_map

    # eventually supply collection name instead of hashmap explicitly and store collections as properties
    def download_dataset(self, dset_map: dict, name: str):
        aws_hash = requests.post(
            "https://api.cellxgene.cziscience.com/dp/v1/datasets/" + dset_map[name]["dataset_id"] + "/asset/" +
            dset_map[name]["filetype_id"]).json()
        h5ad_dataset = requests.get(aws_hash["presigned_url"])
        open("../resources/datasets/" + name.replace(" ", "_") + ".h5ad", "wb").write(h5ad_dataset.content)

    # infrastructure for simultaneous collection of all IDs
    async def _get_concurrent(self, url, session):
        try:
            async with session.get(url=url) as response:
                # resp = await response.read()
                resp_json = await response.json()
                print("Successfully got url {}.".format(url))
        except Exception as e:
            print("Unable to get url {} due to {}.".format(url, e.__class__))
        return resp_json

    async def main_concurrent(self, urls):
        async with aiohttp.ClientSession() as session:
            ret = await asyncio.gather(*[self._get_concurrent(url, session) for url in urls])
        print("Finalized all. Return is a list of len {} outputs.".format(len(ret)))
        return ret


if __name__ == "__main__":
    CellxGeneJSONRequests()
