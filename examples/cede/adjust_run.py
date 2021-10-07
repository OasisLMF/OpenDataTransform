

import os
import argparse
import yaml
import subprocess

import pandas as pd

#set assumed encoding
#ENCODE='ISO-8859-1'
#ENCODE='UTF-8'

def parse_arguments():
    """
    Read arguments from command line and check validity.

    :return: arguments
    :dtype: namespace object
    """

    parser = argparse.ArgumentParser(description='transformation adjustments and execution')
    parser.add_argument(
        '-c', '--config', required=True, 
        help='configuration file for adjustment aspects'
    )
    args = parser.parse_args()

    # Check files and directories exist
    if not os.path.exists(args.config):
        raise Exception('config file does not exist.')

    return args

def get_filename(config_file,module):
    """
    Extract filename from config.

    :return: filename
    :dtype: file object
    """
    with open(config_file,'r') as c:
        conf = yaml.safe_load(c)
        filename = conf[module]['options']['path']

    return(filename)

def adjust_yaml(config_file,module):
    with open(config_file,'r') as c:
        conf = yaml.safe_load(c)
        filename = conf[module]['options']['path']

        appended_filename = 'appended_{}'.format(filename)
        adjusted_config = 'adjusted_{}'.format(config_file)

        with open(adjusted_config,'w') as c_out:
            conf[module]['options']['path'] = appended_filename
            yaml.dump(conf, c_out, default_flow_style=False)

    return(adjusted_config)

def factorize_sublimits(df_location,df_account):
    df_location['CondName'] = df_location['ContractID']+'--'+df_location['SublimitArea'] 
    df_cond = df_location[['ContractID','SublimitArea','CondName']].drop_duplicates()
    df_cond['CondNumber'] = pd.factorize(df_cond['CondName'], sort=True)[0]
    df_location = df_location.merge(df_cond)
    df_account = df_account.merge(df_cond)

    return(df_location,df_account)

def pad_codes(df,pad_char,str_len):
    df = df.astype('str')
    cols = df.columns
    padding = ''
    for i in range(str_len):
        padding = '{}{}'.format(padding,pad_char)

    for col in cols:
        df[col] = df[col].apply(lambda x: '{}{}'.format(padding,x)[-str_len:])

    return df

def check_peril(LocPerilsCovered):
    wind_perils = ['AA1','WTC','WW1']
    surge_perils = ['AA1','WSS','WW1']
    wind=surge=False

    for p in wind_perils:
        if p in LocPerilsCovered:
            wind = True

    for p in surge_perils:
        if p in LocPerilsCovered:
            surge = True

    if wind and surge:
        UpdatedLocPerilsCovered = 'WTC;WSS' 
    elif wind and not surge:
        UpdatedLocPerilsCovered = 'WTC'
    elif surge and not wind:
        UpdatedLocPerilsCovered = 'WSS'
    else:
        UpdatedLocPerilsCovered = LocPerilsCovered
    
    return UpdatedLocPerilsCovered

def main():
    """
    Main function: pre-process data -> run transformations -> post process
    
    """
    # Parse arguments from command line
    args = parse_arguments()
    conf = args.config
    
    with open(conf,'r',encoding='utf8') as c:
        conf = yaml.safe_load(c)
        location_file = conf['config']['location_file']
        account_file = conf['config']['account_file']
        reinsurance_file = conf['config']['reinsurance_file']
        location_config_file = conf['config']['location_config_file']
        account_config_file = conf['config']['account_config_file']
        reinsurance_config_file = conf['config']['reinsurance_config_file']
        input_file_encoding = conf['config']['input_file_encoding']
        ara_adjustment = conf['config']['ara_locperilscovered_adjustment']

    #read input files
    df_location = pd.read_csv(location_file,encoding=input_file_encoding)
    df_account = pd.read_csv(account_file,encoding=input_file_encoding)
    df_reinsurance = pd.read_csv(reinsurance_file,encoding=input_file_encoding)

    #factorize sub-limit ref
    df_location, df_account = factorize_sublimits(df_location,df_account)

    #pad construction and occupancy codes
    df_location[['ConstructionCode','OccupancyCode']] = pad_codes(df_location[['ConstructionCode','OccupancyCode']],'0',4)

    #write out updated files
    location_file_out = 'appended_{}'.format(location_file)
    account_file_out = 'appended_{}'.format(account_file)
    reinsurance_file_out = 'appended_{}'.format(reinsurance_file)

    df_location.to_csv(location_file_out,index=False)
    df_account.to_csv(account_file_out,index=False)
    df_reinsurance.to_csv(reinsurance_file_out,index=False)

    #create adjusted yml config file
    yml_loc_adj = adjust_yaml(location_config_file,'extractor')
    yml_acc_adj = adjust_yaml(account_config_file,'extractor')
    yml_reins_adj = adjust_yaml(reinsurance_config_file,'extractor')

    #run transformation
    subprocess.run(['converter', '-c',yml_loc_adj,'run'])
    subprocess.run(['converter', '-c',yml_acc_adj,'run'])
    subprocess.run(['converter', '-c',yml_reins_adj,'run'])

    #reinsurance - split oed files
    transformed_reins_file = get_filename(yml_reins_adj,'loader')
    df_oed_reinsurance = pd.read_csv(transformed_reins_file)
    ri_info_fields = ['ReinsNumber','ReinsLayerNumber','ReinsPeril','RiskLimit','RiskAttachment','ReinsName','ReinsCurrency','ReinsType']
    ri_scope_fields = ['PortNumber','AccNumber','ReinsNumber','LocNumber','CedantName','CededPercent','RiskLevel']
    df_ri_info = df_oed_reinsurance[ri_info_fields]
    df_ri_scope = df_oed_reinsurance[ri_scope_fields]

    ri_info_file_out = transformed_reins_file.replace('.csv','_info.csv')
    ri_scope_file_out = transformed_reins_file.replace('.csv','_scope.csv')

    df_ri_info.to_csv(ri_info_file_out,index=False)
    df_ri_scope.to_csv(ri_scope_file_out,index=False)

    os.remove(transformed_reins_file)

    #post adjust for ARA
    if ara_adjustment:
        transformed_loc_file = get_filename(yml_loc_adj,'loader')
        df_location = pd.read_csv(transformed_loc_file)
        df_location['LocPerilsCovered'] = df_location['LocPerilsCovered'].apply(lambda x: check_peril(x))
        df_location.to_csv(transformed_loc_file,index=False)

    





if __name__ == "__main__":
    main()
