#!/usr/bin/env python
import minio
import os
import sys

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple


class Apportionment(ABC):
    """Abstract class representing a method of counting votes."""

    @abstractmethod
    def load_data(self, district_results, candadates_results) -> None:
        """Loads the data about the results of the elections."""
        pass

    @abstractmethod
    def calculate(self) -> Tuple[Dict[str, int], Dict[Any, Any]]:
        """Calculates the results of the elections.

        Returns:
            Dict[str, int]: The number of votes for each party.
            Dict[Any, Any]: The additional information about the results, specific to the method.
        """
        pass

# TODO: implement methods


def select_method(method: str) -> Apportionment:
    """Selects the method of counting votes based on the name."""
    if method == "sainte_lague":
        raise NotImplementedError()
    if method == "hondt":
        raise NotImplementedError()
    
    # Method not implemented:
    raise NotImplementedError()

def init_minio() -> minio.Minio:
    key = os.environ["MINIO_ACCESS_KEY"]
    secret = os.environ["MINIO_SECRET_KEY"]
    pass

def save_results(minio_client: minio.Minio, votes: Dict[str, int], info: Dict[Any, Any]) -> None:
    pass


def main() -> None:
    apportionment = select_method(sys.argv[1])
    minio_client = init_minio()
    district_results = None # TODO: get district results from minio
    candadates_results = None # TODO: get candadates results from minio
    apportionment.load_data(district_results, candadates_results)
    votes, info = apportionment.calculate()
    save_results(minio_client, votes, info)


if __name__ == "__main__":
    main()
