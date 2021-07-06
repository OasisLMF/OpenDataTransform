

import os
import argparse
import yaml
import subprocess


import pandas as pd

#set assumed encoding
ENCODE='ISO-8859-1'


def parse_arguments():
    """
    Read arguments from command line and check validity.

    :return: arguments
    :dtype: namespace object
    """

    parser = argparse.ArgumentParser(description='transformation adjustments and execution')
    parser.add_argument(
        '-l', '--location_file', required=True, 
        help='The location file'
    )
    parser.add_argument(
        '-a', '--account_file', required=True, 
        help='The account file'
    )
    parser.add_argument(
        '-cl', '--location_config_file', required=True, 
        help='The location config file'
    )
    parser.add_argument(
        '-ca', '--account_config_file', required=True, 
        help='The account config file'
    )
    args = parser.parse_args()

    # Check files and directories exist
    if not os.path.exists(args.location_file):
        raise Exception('location file does not exist.')

    if not os.path.exists(args.account_file):
        raise Exception('account file does not exist.')

    if not os.path.exists(args.location_config_file):
        raise Exception('location config file does not exist.')

    if not os.path.exists(args.account_config_file):
        raise Exception('account config file does not exist.')

    return args

def get_filename(config_file):
    ###not used
    """
    Extract filename from config.

    :return: filename
    :dtype: file object
    """
    with open(config_file,'r') as c:
        conf = yaml.safe_load(c)
        filename = conf['extractor']['options']['path']

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

def main():
    """
    Main function: pre-process data -> run transformations -> post process
    
    """
    # Parse arguments from command line
    args = parse_arguments()

    location_file = args.location_file
    account_file = args.account_file

    #read input files
    df_location = pd.read_csv(location_file,encoding=ENCODE)
    df_account = pd.read_csv(account_file,encoding=ENCODE)

    #factorize sub-limit ref
    df_location, df_account = factorize_sublimits(df_location,df_account)

    #pad construction and occupancy codes
    df_location[['ConstructionCode','OccupancyCode']] = pad_codes(df_location[['ConstructionCode','OccupancyCode']],'0',4)
    print(df_location[['ConstructionCode','OccupancyCode']])


    #write out updated files
    location_file_out = 'appended_{}'.format(location_file)
    account_file_out = 'appended_{}'.format(account_file)

    df_location.to_csv(location_file_out,index=False)
    df_account.to_csv(account_file_out,index=False)

    #create adjusted yml config file
    location_config_file = args.location_config_file
    yml_adj = adjust_yaml(location_config_file,'extractor')

    #run transformation
    subprocess.run(['converter', '-c',yml_adj,'run'])




if __name__ == "__main__":
    main()
