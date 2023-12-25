#!/usr/bin/env python
import minio
import os
import sys

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple
import pandas as pd

import minio_communication
from DivisorMethods import * 

CONSTITUENCIES = 41

class Apportionment(ABC):
    """Abstract class representing a method of counting votes."""

    #To chyba powinno byc wspolne dla wszystkich metod
    def load_data(self, district_results, candadates_results) -> None:
        """Loads the data about the results of the elections."""

        # Data from https://wybory.gov.pl/sejmsenat2023/pl/dane_w_arkuszach
        # te dwa ready to argumenty z minio
        df = pd.read_csv('wyniki.csv', sep=";").fillna(0)
        parties = pd.concat([df, df.apply(['sum'])]).iloc[:, 25:].set_index([pd.Index(range(1, CONSTITUENCIES + 2))])
        constituences = pd.read_csv('okregi.csv', sep=";").iloc[:, [0,1,5,6]].set_index('Numer okręgu')

        # Joining results with constituences information
        ed = constituences.join(parties) # election data
        ed = pd.concat([ed, ed.apply(['sum'])]) #tofix string concat 

        # Calculating which comitties pass the threshold
        comitties = [ele for ele in list(ed.columns) if 'KOMITET' in ele]
        comitties = [ele for ele in comitties if self.pass_threshold(ele)]

        self.SEATS = ed.loc['sum']['Liczba mandatów']
        self.VOTES = ed.loc['sum']['Liczba głosów ważnych oddanych łącznie na wszystkie listy kandydatów']
        self.comitties = comitties
        self.ed = ed
        # Zapisac SEATS,VOTES,comitties i election data w obiekcie

    # Checking if given party can participate in seats allocation
    def pass_threshold(self, committy) -> bool:
        supp_share = 100 * self.ed.loc['sum'][committy] / self.ed.loc['sum']['Liczba głosów ważnych oddanych łącznie na wszystkie listy kandydatów']
        threshold = 5 # Regular Committy
        if 'KOALICYJNY' in committy: 
            threshold = 8 # Coalition Committy
        if 'MNIEJSZOŚĆ' in committy:
            threshold = 0 # Minority Commity
        return threshold <= supp_share


    @abstractmethod
    def calculate(self) -> Tuple[Dict[str, int], Dict[Any, Any]]:
        """Calculates the results of the elections.

        Returns:
            Dict[str, int]: The number of seats for each party.
            Dict[Any, Any]: The additional information about the results, specific to the method.
        """
        pass


# Current system
class ConstituencialDHondt(Apportionment): 
    def calculate(self) -> Tuple[Dict[str, int], Dict[Any, Any]]:
        sum_parties = dict([(name, 0) for name in self.comitties])
        last_seat_data = {}

        for id in range(1, CONSTITUENCIES + 1):
            data, seats, cname = None # Read from minio TODO
            result, last_win_info = runDHondt(data, seats)
            for (key, val) in result:
                sum_parties[key] += val

            last_seat_data[f"C-{id} ({cname})"] = last_win_info

        return (sum_parties, last_seat_data)


class GlobalDHondt(Apportionment): 
    def calculate(self) -> Tuple[Dict[str, int], Dict[Any, Any]]: 
        data_global = [(com, self.ed.loc["sum"][com]) for com in self.comitties]
        result, last_seat_data = runDHondt(data_global, self.SEATS)
        return (result, {"last_seat_data":last_seat_data}) 


class SquaredDHondt(Apportionment): 
    def calculate(self) -> Tuple[Dict[str, int], Dict[Any, Any]]: 
        data_global = [(com, self.ed.loc["sum"][com]) for com in self.comitties]
        sum_votes = sum(val for (_,val) in data_global)
        data_global_sq = [(com, val * (1 + val/sum_votes)) for (com, val) in data_global]
        result, last_seat_data = runDHondt(data_global_sq, self.SEATS)
        return (result, {"last_seat_data":last_seat_data})


class ConstituencialSainteLague(Apportionment):
    def calculate(self) -> Tuple[Dict[str, int], Dict[Any, Any]]:
        sum_parties = dict([(name, 0) for name in self.comitties])

        for id in range(1, CONSTITUENCIES + 1):
            data, seats, cname = None # Read from minio TODO
            result, _ = runDHondt(data, seats)
            for (key, val) in result:
                sum_parties[key] += val

        return (sum_parties, None)


class GlobalSainteLague(Apportionment): 
    def calculate(self) -> Tuple[Dict[str, int], Dict[Any, Any]]: 
        data_global = [(com, self.ed.loc["sum"][com]) for com in self.comitties]
        result, last_seat_data = runSainteLague(data_global, self.SEATS)
        return (result, {"last_seat_data":last_seat_data})  


class FairVoteWeightDhonth(Apportionment):
    def calculate(self):
        self.ed['True proportion'] = self.ed['Liczba głosów ważnych oddanych łącznie na wszystkie listy kandydatów'] * self.SEATS / self.VOTES
        self.ed['Voter Strength'] = 100*self.ed['Liczba mandatów'] / self.ed['True proportion'] - 100
        worst = self.ed.sort_values('Voter Strength').iloc[0]
        best = self.ed.sort_values('Voter Strength').iloc[-1]
        diff = float((best['Voter Strength'] + 100) / ((worst['Voter Strength'] + 100)))
        result1 = (f"Voters in {best['Siedziba OKW']} have vote {round(diff, 4)}x as strong as voters in {worst['Siedziba OKW']}")
        full_comparison1 = self.ed.sort_values('Voter Strength').iloc[:, [2,0,16,17]]
        
        paramHM = self.find_HMpar(self)
        self.ed['Liczba mandatów'] = self.ed['True proportion'].apply(lambda x: round(x + paramHM))

        # Updated voter strength
        self.ed['Voter Strength'] = 100*self.ed['Liczba mandatów'] / self.ed['True proportion'] - 100
        worst = self.ed.sort_values('Voter Strength').iloc[0]
        best = self.ed.sort_values('Voter Strength').iloc[-1]
        diff = float((best['Voter Strength'] + 100) / ((worst['Voter Strength'] + 100)))
        
        result2 = (f"Voters in {best['Siedziba OKW']} have vote {round(diff, 4)}x as strong as voters in {worst['Siedziba OKW']}")
        full_comparison2 = self.ed.sort_values('Voter Strength').iloc[:, [2,0,16,17]]

        sum_parties = dict([(name, 0) for name in self.comitties])
        extra_data = {}
        extra_data["Vote Strength before"] = result1
        extra_data["Vote Strength after"] = result2 
        extra_data["Full comparison befere"] = full_comparison1
        extra_data["Full comparison after"] = full_comparison2

        for id in range(1, CONSTITUENCIES + 1):
            data, seats, cname = None
            result, _ = runDHondt(data, seats)
            for (key, val) in result:
                sum_parties[key] += val
        
        return (sum_parties, extra_data)


    # Hare-Nemayer rounding
    def find_HMpar(self):
        low = -1
        high = 1
        while True:
            p = (low + high) / 2 
            val = self.ed['True proportion'].apply(lambda x: round(x + p)).sum()
            
            if val == self.SEATS * 2:
                return p
            elif val < self.SEATS * 2:
                low = p
            else:
                high = p


def select_method(method: str) -> Apportionment:
    """Selects the method of counting votes based on the name."""
    if method == "sainte_lague":
        return ConstituencialSainteLague()
    if method == "dhondt":
        raise NotImplementedError()
    
    # Method not implemented:
    raise NotImplementedError()


def save_results(minio_client: minio.Minio, votes: Dict[str, int], info: Dict[Any, Any]) -> None:
    pass


def main() -> None:
    apportionment = select_method(sys.argv[1])
    minio_client = minio_communication.get_client()
    district_results = None # TODO: get district results from minio
    candadates_results = None # TODO: get candadates results from minio
    apportionment.load_data(district_results, candadates_results)
    votes, info = apportionment.calculate()
    save_results(minio_client, votes, info)


if __name__ == "__main__":
    main()
