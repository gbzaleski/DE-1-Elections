#!/usr/bin/env python

import argparse
import io
import json
import minio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple
import pandas as pd

import minio_communication
from DivisorMethods import * 
from consts import *


class Apportionment(ABC):
    """Abstract class representing a method of counting votes."""

    @staticmethod
    @abstractmethod
    def name() -> str:
        pass

    def load_data(self, year, results, districts) -> None:
        """Loads the data about the results of the elections."""

        # Data from https://wybory.gov.pl/sejmsenat2023/pl/dane_w_arkuszach
        # te dwa ready to argumenty z minio
        df = results.fillna(0)
        idx = 23 if year == 2019 else 25
        idxs = [0,1,2,6] if year == 2019 else [0,1,5,6]
        parties = pd.concat([df, df.apply(['sum'])]).iloc[:, idx:].set_index([pd.Index(range(1, CONSTITUENCIES + 2))])
        constituences = districts.iloc[:, idxs].set_index('Numer okręgu')

        # Joining results with constituences information
        ed = constituences.join(parties) # election data
        ed = pd.concat([ed, ed.apply(['sum'])]) #tofix string concat 

        # Calculating which comitties pass the threshold
        comitties = [ele for ele in list(ed.columns) if 'KOMITET' in ele]
        comitties = [ele for ele in comitties if self.pass_threshold(ele, ed)]

        self.SEATS = ed.loc['sum']['Liczba mandatów']
        self.VOTES = ed.loc['sum']['Liczba głosów ważnych oddanych łącznie na wszystkie listy kandydatów']
        self.comitties = comitties
        self.ed = ed

    # Checking if given party can participate in seats allocation
    # Default polish threshold, can be overriden in child classes
    def pass_threshold(self, committy, ed) -> bool:
        supp_share = 100 * ed.loc['sum'][committy] / ed.loc['sum']['Liczba głosów ważnych oddanych łącznie na wszystkie listy kandydatów']
        threshold = 5 # Regular Committy
        if 'KOALICYJNY' in committy: 
            threshold = 8 # Coalition Committy
        if 'MNIEJSZOŚĆ' in committy:
            threshold = 0 # Minority Commity
        return threshold <= supp_share

    # Reads voting results from one constituency
    def read_constituency_info(self, id): 
        row = self.ed.loc[id]
        cname = row['Siedziba OKW']
        seats = row['Liczba mandatów']
        data = [(name, row[name]) for name in self.comitties]
        return (data, seats, cname)

    @abstractmethod
    def calculate(self) -> Tuple[Dict[str, int], Dict[Any, Any]]:
        """Calculates the results of the elections.

        Returns:
            Dict[str, int]: The number of seats for each party.
            Dict[Any, Any]: The additional information about the results, specific to the method.
        """
        pass


    @staticmethod
    def encode_number_of_seats_in_df(seats: Dict[str, int]) -> pd.DataFrame:
        return pd.DataFrame(list(seats.items()), columns=['party', 'seats'])


# Current system
class ConstituencialDHondt(Apportionment):
    @staticmethod
    def name() -> str:
        return "constituencial-dhondt"

    def calculate(self) -> Tuple[Dict[str, int], Dict[Any, Any]]:
        sum_parties = dict([(name, 0) for name in self.comitties])
        last_seat_data = {}

        for id in range(1, CONSTITUENCIES + 1):
            data, seats, cname = self.read_constituency_info(id)
            result, last_win_info = runDHondt(data, seats)
            for (key, val) in result:
                sum_parties[key] += val

            last_seat_data[f"C-{id} ({cname})"] = last_win_info

        return (sum_parties, last_seat_data)

class ConstituencialDHondtNoThreshold(ConstituencialDHondt):
    @staticmethod
    def name() -> str:
        return "constituencial-dhondt-no-threshold"

    def pass_threshold(self, committy, ed) -> bool:
        return True


class GlobalDHondt(Apportionment): 
    @staticmethod
    def name() -> str:
        return "global-dhondt"


    def calculate(self) -> Tuple[Dict[str, int], Dict[Any, Any]]:
        data_global = [(com, self.ed.loc["sum"][com]) for com in self.comitties]
        result, last_seat_data = runDHondt(data_global, self.SEATS)
        return (result, {"last_seat_data":last_seat_data})


class GlobalDHondtNoThreshold(GlobalDHondt):
    @staticmethod
    def name() -> str:
        return "global-dhondt-no-threshold"

    def pass_threshold(self, committy, ed) -> bool:
        return True


class SquaredDHondt(Apportionment): 
    @staticmethod
    def name() -> str:
        return "squared-dhondt"


    def calculate(self) -> Tuple[Dict[str, int], Dict[Any, Any]]:
        data_global = [(com, self.ed.loc["sum"][com]) for com in self.comitties]
        sum_votes = sum(val for (_,val) in data_global)
        data_global_sq = [(com, val * (1 + val/sum_votes)) for (com, val) in data_global]
        result, last_seat_data = runDHondt(data_global_sq, self.SEATS)
        return (result, {"last_seat_data":last_seat_data})


class ConstituencialSainteLague(Apportionment):
    @staticmethod
    def name() -> str:
        return "constituencial-sainte-lague"


    def calculate(self) -> Tuple[Dict[str, int], Dict[Any, Any]]:
        sum_parties = dict([(name, 0) for name in self.comitties])

        for id in range(1, CONSTITUENCIES + 1):
            data, seats, cname = self.read_constituency_info(id)
            result, _ = runSainteLague(data, seats)
            for (key, val) in result:
                sum_parties[key] += val

        return (sum_parties, None)


class ConstituencialSainteLagueNoThreshold(ConstituencialSainteLague):
    @staticmethod
    def name() -> str:
        return "constituencial-sainte-lague-no-threshold"

    def pass_threshold(self, committy, ed) -> bool:
        return True


class GlobalSainteLague(Apportionment):
    @staticmethod
    def name() -> str:
        return "global-sainte-lague"


    def calculate(self) -> Tuple[Dict[str, int], Dict[Any, Any]]:
        data_global = [(com, self.ed.loc["sum"][com]) for com in self.comitties]
        result, _ = runSainteLague(data_global, self.SEATS)
        return (result, None)  


class GlobalSainteLagueNoThreshold(GlobalSainteLague):
    @staticmethod
    def name() -> str:
        return "global-sainte-lague-no-threshold"

    def pass_threshold(self, committy, ed) -> bool:
        return True


class FairVoteWeightDHondt(Apportionment):
    @staticmethod
    def name() -> str:
        return "fair-vote-weight-dhondt"

    def calculate(self):
        self.ed['True proportion'] = self.ed['Liczba głosów ważnych oddanych łącznie na wszystkie listy kandydatów'] * self.SEATS / self.VOTES
        self.ed['Voter Strength'] = 100*self.ed['Liczba mandatów'] / self.ed['True proportion'] - 100
        worst = self.ed.sort_values('Voter Strength').iloc[0]
        best = self.ed.sort_values('Voter Strength').iloc[-1]
        diff = float((best['Voter Strength'] + 100) / ((worst['Voter Strength'] + 100)))
        result1 = (f"Voters in {best['Siedziba OKW']} have vote {round(diff, 4)}x as strong as voters in {worst['Siedziba OKW']}")
        full_comparison1 = self.ed.sort_values('Voter Strength').iloc[:, [2,0,16,17]]
        
        # Updating seat allocation
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
            data, seats, cname = self.read_constituency_info(id)
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
    if method == ConstituencialSainteLague.name():
        return ConstituencialSainteLague()
    if method == GlobalSainteLague.name():
        return GlobalSainteLague()
    if method == ConstituencialDHondt.name():
        return ConstituencialDHondt()
    if method == GlobalDHondt.name():
        return GlobalDHondt()
    if method == SquaredDHondt.name():
        return SquaredDHondt()
    if method == FairVoteWeightDHondt.name():
        return FairVoteWeightDHondt()
    if method == ConstituencialSainteLagueNoThreshold.name():
        return ConstituencialSainteLagueNoThreshold()
    if method == GlobalSainteLagueNoThreshold.name():
        return GlobalSainteLagueNoThreshold()
    if method == ConstituencialDHondtNoThreshold.name():
        return ConstituencialDHondtNoThreshold()
    if method == GlobalDHondtNoThreshold.name():
        return GlobalDHondtNoThreshold()
    
    raise NotImplementedError(method)


def additional_info_obj_name(apportionment) -> str:
    return f"{apportionment.name()}-additional-info.json"


def seats_obj_name(apportionment) -> str:
    return f"{apportionment.name()}-seats.csv"


def write_dict_json_to_minio(minio_client, bucket_name, object_name, dict_to_write):
    json_string_bytes = json.dumps(dict_to_write).encode("utf-8")
    minio_client.put_object(
        bucket_name,
        object_name,
        io.BytesIO(json_string_bytes),
        len(json_string_bytes),
        content_type='application/json'
    )

def write_csv_bytes_to_minio(minio_client, bucket_name, object_name, df):
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False, encoding="utf-8")

    buffer_bytes = buffer.getvalue()

    minio_client.put_object(bucket_name, object_name,
                            io.BytesIO(buffer_bytes), len(buffer_bytes), content_type='text/csv')


def save_results(minio_client: minio.Minio, bucket_configuration: minio_communication.MinioBucketConfigurationForYear, apportionment: Apportionment, seats: Dict[str, int], additional_info: Dict[Any, Any]) -> None:
    minio_communication.create_bucket_if_not_exist(minio_client, bucket_configuration.transformed_data_bucket)

    write_dict_json_to_minio(minio_client, bucket_configuration.transformed_data_bucket, additional_info_obj_name(apportionment), additional_info)
    write_csv_bytes_to_minio(minio_client, bucket_configuration.transformed_data_bucket, seats_obj_name(apportionment), apportionment.encode_number_of_seats_in_df(seats))

def load_districts(minio_client, bucket_configuration: minio_communication.MinioBucketConfigurationForYear, year):
    response = minio_client.get_object(bucket_configuration.raw_data_bucket, FILENAMES_BY_YEAR[year]["districts"])
    csv_data = pd.read_csv(io.BytesIO(response.read()), sep=";")
    return csv_data


def load_results(minio_client, bucket_configuration: minio_communication.MinioBucketConfigurationForYear, year):
    response = minio_client.get_object(bucket_configuration.raw_data_bucket, FILENAMES_BY_YEAR[year]["results"])
    csv_data = pd.read_csv(io.BytesIO(response.read()), sep=";")
    return csv_data

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', type=int, choices=YEARS, default=2023,
                        help='year to analyze')
    parser.add_argument('--apportionment', type=str, default=ConstituencialSainteLague.name(),
                        help='apportionment')
    return parser.parse_args()

def main() -> None:
    program_args = parse_args()
    apportionment = select_method(program_args.apportionment)
    minio_client = minio_communication.get_client()
    bucket_configuration = minio_communication.get_minio_bucket_configuration(program_args.year)

    districts = load_districts(minio_client, bucket_configuration, program_args.year)
    results = load_results(minio_client, bucket_configuration, program_args.year)

    apportionment.load_data(program_args.year, results, districts)
    seats, info = apportionment.calculate()
    save_results(minio_client, bucket_configuration, apportionment, seats, info)

if __name__ == "__main__":
    main()
