from pathlib import Path
from dataclasses import dataclass, asdict, field
from .prompts import Prompts
src_path = Path(__file__).parent.resolve()
assert src_path.stem == 'src', "`src_path` must end with 'src'"

@dataclass
class ServersConfig:
    server_name: str = ''
    server_name_full: str = ''
    description: str = ''   # Server description
    data_dict_filenames: list[str] = field(default_factory=list)
    db_filename: str = ''
    host: str = '0.0.0.0'   # Host address (0.0.0.0 allows connections from any IP)
    port: int = 9999        # Port number for the server
    servers_path: str = str(src_path / 'servers')
    data_path: str = str(src_path.parent / 'data')

    def asdict(self):
        """Convert the dataclass to a dictionary."""
        return asdict(self)

    @classmethod
    def geodomain(cls):
        return cls(
            server_name='geodomain',
            server_name_full='Geospatial Domain',
            data_dict_filenames=[
                'broadband_coverage-data_dictionary.json',
                'broadband_speed-data_dictionary.json',
                'cowz_description-data_dictionary.json',
                'cowz-data_dictionary.json',
                'house_age-data_dictionary.json',
                'house_med_trans-data_dictionary.json',
                'imd-data_dictionary.json',
                'oa_mosa_lad_rgn-data_dictionary.json',
                'poi-data_dictionary.json',
                'population-data_dictionary.json',
                'rmi_base2023-data_dictionary.json',
                'spatial_signatures-data_dictionary.json'
            ],
            db_filename='geodomain.db',
            description='Geospatial Domain Data Server',
            port=8111
        )
    
    @classmethod
    def openstreetmap(cls):
        return cls(
            server_name='openstreetmap',
            server_name_full='Open Street Map',
            description='OpenStreetMap Data Server',
            port=8112
        )
    
    @classmethod
    def national_policy_planning_framework(cls):
        return cls(
            server_name='national_policy_planning_framework',
            server_name_full='National Policy Planning Framework',
            description='National Policy Planning Framework Data Server',
            port=8113
        )