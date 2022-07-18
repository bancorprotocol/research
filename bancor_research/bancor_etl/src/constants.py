# coding=utf-8
import numpy as np

# base google sheet name to increment tableau wildcard * union on
EVENTS_TABLE = 'all_events'

# Created via Google Cloud Admin Console
FORCE_RATE_THROTTLE = False
SLEEP_TIME = 100
GOOGLE_SHEETS_CREDENTIALS = '/dbfs/FileStore/tableau/bancor_research_e92ff2450ca7.json'

# Required google sheets email sharing permissions with:
ROBOT_EMAIL = "bancor-research@bancor-research.iam.gserviceaccount.com"
USER_EMAIL = "bancor.research@gmail.com"

# Containers to be filled-in during processing
ALL_COLUMNS = []
DEFAULT_VALUE_MAP_CP = {}
DEFAULT_VALUE_MAP = {}

# See https://support.google.com/drive/answer/37603
GOOGLE_SHEETS_MAX_CELLS = 10000000
GOOGLE_SHEETS_MAX_COLUMNS = 18278

# Google sheet chunk size will start here, then dynamically increment down by 1000 rows until a csv filesize of less than 10MB requirement is met
TABLEAU_MANAGEABLE_ROWS = 24000

# Address columns can optionally be encoded to save space and improve tableau performance. These are the columns which will be encoded. If list is empty, no encoding will be performed.
ADDRESS_COLUMNS = [
    # 'contextId', 'pool', 'txhash', 'provider'
]

# Maps the google sheets data dictionary to python/pandas types and fillna values
REPLACE_WITH_NA = ['0E+18', '<NA>']

# Maps the google sheets data dictionary to python/pandas types and fillna values
TYPE_MAP = {
    'decimal': {
        'type': str,
        'fillna': '0.0'
    },
    'integer': {
        'type': int,
        'fillna': 0
    },
    'string': {
        'type': str,
        'fillna': np.nan
    },
    'datetime': {
        'type': 'datetime64[ns]',
        'fillna': np.nan
    },
    'bool': {
        'type': bool,
        'fillna': np.nan
    },
}

# COMMAND ----------

LIST_OF_SPARK_TABLES = [
    # Add new table names here (see instructions at top of notebook)

    # NEW TABLES -> implemented on July 5, 2022
    'events_all_tokensdeposited_csv',
    'events_bancornetwork_flashloancompleted_csv',
    'events_bancornetwork_fundsmigrated_csv',
    'events_bancornetwork_networkfeeswithdrawn_csv',
    'events_bancornetwork_pooladded_csv',
    'events_bancornetwork_poolcollectionadded_csv',
    'events_bancornetwork_poolcollectionremoved_csv',
    'events_bancornetwork_poolcreated_csv',
    'events_bancornetwork_poolremoved_csv',
    'events_bancornetwork_tokenstraded_csv',
    'events_bancornetwork_tokenstraded_updated_csv',
    'events_bancorportal_sushiswappositionmigrated_csv',
    'events_bancorportal_uniswapv2positionmigrated_csv',
    'events_bancorv1migration_positionmigrated_csv',
    'events_bntpool_fundingrenounced_csv',
    'events_bntpool_fundingrequested_csv',
    'events_bntpool_fundsburned_csv',
    'events_bntpool_fundswithdrawn_csv',
    'events_bntpool_tokensdeposited_csv',
    'events_bntpool_tokenswithdrawn_csv',
    'events_bntpool_totalliquidityupdated_csv',
    'events_externalprotectionvault_fundsburned_csv',
    'events_externalprotectionvault_fundswithdrawn_csv',
    'events_externalrewardsvault_fundsburned_csv',
    'events_externalrewardsvault_fundswithdrawn_csv',
    'events_mastervault_fundsburned_csv',
    'events_mastervault_fundswithdrawn_csv',
    'events_networksettings_defaultflashloanfeeppmupdated_csv',
    'events_networksettings_flashloanfeeppmupdated_csv',
    'events_networksettings_fundinglimitupdated_csv',
    'events_networksettings_minliquidityfortradingupdated_csv',
    'events_networksettings_tokenaddedtowhitelist_csv',
    'events_networksettings_tokenremovedfromwhitelist_csv',
    'events_networksettings_vortexburnrewardupdated_csv',
    'events_networksettings_withdrawalfeeppmupdated_csv',
    'events_pendingwithdrawals_withdrawalcancelled_csv',
    'events_pendingwithdrawals_withdrawalcompleted_csv',
    'events_pendingwithdrawals_withdrawalcurrentpending_csv',
    'events_pendingwithdrawals_withdrawalinitiated_csv',
    'events_poolcollection_defaulttradingfeeppmupdated_csv',
    'events_poolcollection_depositingenabled_csv',
    'events_poolcollection_tokensdeposited_csv',
    'events_poolcollection_tokenswithdrawn_csv',
    'events_poolcollection_totalliquidityupdated_csv',
    'events_poolcollection_tradingenabled_csv',
    'events_poolcollection_tradingfeeppmupdated_csv',
    'events_poolcollection_tradingliquidityupdated_csv',
    'events_pooldata_historical_latest_csv',
    'events_stakingrewardsclaim_rewardsclaimed_csv',
    'events_stakingrewardsclaim_rewardsstaked_csv',
    'events_standardrewards_programcreated_csv',
    'events_standardrewards_programenabled_csv',
    'events_standardrewards_programterminated_csv',
    'events_standardrewards_providerjoined_csv',
    'events_standardrewards_providerleft_csv',
    'events_standardrewards_rewardsclaimed_csv',
    'events_standardrewards_rewardsstaked_csv',
    'events_v3_daily_bnttradingliquidity_csv',
    'events_v3_historical_deficit_by_tkn_csv',
    'events_v3_historical_deficit_csv',
    'events_v3_historical_spotrates_emarates_csv',
    'events_v3_historical_tradingliquidity_csv',
    'events_versiontwo_tokenstraded_csv'
]

# COMMAND ----------

UNUSED_EVENTS = [
    'poolcollection_defaulttradingfeeppmupdated_csv',
    'events_poolcollection_depositingenabled_csv',
    'events_poolcollection_totalliquidityupdated_csv',
    'events_poolcollection_tradingfeeppmupdated_csv',
    'events_poolcollection_tradingliquidityupdated_csv',
    'events_stakingrewardsclaim_rewardsclaimed_csv',
    'events_stakingrewardsclaim_rewardsstaked_csv',
    'events_standardrewards_programcreated_csv',
    'events_standardrewards_programenabled_csv',
    'events_standardrewards_programterminated_csv',
    'events_standardrewards_providerjoined_csv',
    'events_standardrewards_providerleft_csv',
    'events_standardrewards_rewardsclaimed_csv',
    'events_standardrewards_rewardsstaked_csv',
    'events_poolcollection_tradingliquidityupdated_spotrates_csv',
]
