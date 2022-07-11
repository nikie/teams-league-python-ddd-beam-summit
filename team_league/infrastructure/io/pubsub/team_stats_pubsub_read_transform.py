import json
from typing import Dict

import apache_beam as beam
from apache_beam import PTransform
from apache_beam.io import ReadFromPubSub
from apache_beam.pvalue import PBegin
from dacite import from_dict

from team_league.application.team_league_options import TeamLeagueOptions
from team_league.domain.team_stats_raw import TeamStatsRaw


class TeamStatsPubSubReadTransform(PTransform):

    def __init__(self,
                 pipeline_options: TeamLeagueOptions):
        super().__init__()
        self.pipeline_options = pipeline_options

    def expand(self, inputs: PBegin):
        return (inputs |
                'Read team stats from pub sub' >> ReadFromPubSub(topic=self.pipeline_options.input_subscription) |
                'Map str message to Dict' >> beam.Map(self.to_dict) |
                'Deserialize Dict to domain dataclass' >> beam.Map(self.deserialize))

    def to_dict(self, team_stats_raw_as_str: str) -> Dict:
        return json.loads(team_stats_raw_as_str)

    def deserialize(self, team_stats_raw_as_dict: Dict) -> TeamStatsRaw:
        return from_dict(
            data_class=TeamStatsRaw,
            data=team_stats_raw_as_dict
        )
