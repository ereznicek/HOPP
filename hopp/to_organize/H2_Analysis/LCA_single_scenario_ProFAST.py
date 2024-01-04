# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 12:09:20 2022

@author: ereznic2
"""
import pandas as pd
import numpy as np
import os.path

# grid_connection_scenario = 'hybrid-grid'
# atb_year = 2020
# site_name = 'TX'
# turbine_model = '6MW'
# electrolysis_scale = 'Centralized'
# policy_option = 'no policy'
# grid_price_scenario = 'retail-flat'
# electrolyzer_energy_kWh_per_kg = 55

def hydrogen_LCA_singlescenario_ProFAST(grid_connection_scenario,atb_year,site_name,policy_option,hydrogen_production_while_running,H2_Results,electrolyzer_energy_kWh_per_kg,solar_size_mw,storage_size_mw,hopp_dict,H2_PTC_duration):

    dircambium = os.path.join(hopp_dict.main_dict["Configuration"]["parent_path"], "H2_Analysis", "Cambium_data", "Cambium22_MidCase100by2035_hourly_")

    dirgreet = os.path.join(hopp_dict.main_dict["Configuration"]["parent_path"], "H2_Analysis","greet_emission_intensities.csv")
    #==============================================================================
    # DATA
    #==============================================================================
    # Conversions
    g_to_kg_conv  = 0.001  # Conversion from grams to kilograms
    kg_to_MT_conv = 0.001 # Converion from kg to metric tonnes
    MT_to_kg_conv = 1000 # Conversion from metric tonne to kilogram
    kWh_to_MWh_conv = 0.001 # Conversion from kWh to MWh

    #------------------------------------------------------------------------------
    # Renewable infrastructure embedded emission intensities
    #------------------------------------------------------------------------------
    #system_life        = plant_life
    ely_stack_capex_EI = 0.019 # PEM electrolyzer CAPEX emissions (kg CO2e/kg H2)
    wind_capex_EI      = 10    # Electricity generation capacity from wind, nominal value taken (g CO2e/kWh)
    if solar_size_mw != 0:
        solar_pv_capex_EI = 37     # Electricity generation capacity from solar pv, nominal value taken (g CO2e/kWh)
    else:
        solar_pv_capex_EI = 0   # Electricity generation capacity from solar pv, nominal value taken (g CO2e/kWh)

    if storage_size_mw != 0:
        battery_EI = 20             # Electricity generation capacity from battery (g CO2e/kWh)
    else:
        battery_EI = 0  # Electricity generation capacity from battery (g CO2e/kWh)

    # Emission factors
    greet_ei = pd.read_csv(dirgreet,index_col = None,header=0)
    emitting_technologies = greet_ei.loc[:,'Technology'].tolist()
    greet_ei = greet_ei.set_index('Technology')

    #------------------------------------------------------------------------------
    # Hydrogen production via water electrolysis
    #------------------------------------------------------------------------------

    grid_trans_losses   = 0.05 # Grid losses of 5% are assumed (-)
    fuel_to_grid_curr   = 48   # Fuel mix emission intensity for current power grid (g CO2e/kWh)
    fuel_to_grid_futu   = 14   # Fuel mix emission intensity for future power grid (g CO2e/kWh)

    if atb_year == 2020:
        cambium_year = 2025
    elif atb_year == 2025:
        cambium_year = 2030
    elif atb_year == 2030:
        cambium_year =2035
    elif atb_year == 2035:
        cambium_year = 2040
    
 
    energy_from_grid_df = pd.DataFrame(hopp_dict.main_dict["Models"]["grid"]["ouput_dict"]['energy_from_the_grid'],columns=['Energy from the grid (kWh)'])
    energy_from_renewables_df = pd.DataFrame(hopp_dict.main_dict["Models"]["grid"]["ouput_dict"]['energy_from_renewables'],columns=['Energy from renewables (kWh)'])
    # Read in Cambium data

    emission_intensity_grid = []
    emission_intensity_offgrid = []
    years = list(range(cambium_year,2055,5))
    for year in years:
        cambiumdata_filepath = dircambium + site_name + '_'+str(year) + '.csv'
        # cambium_data = pd.read_csv(cambiumdata_filepath,index_col = None,header = 5,usecols = ['lrmer_co2_c','lrmer_ch4_c','lrmer_n2o_c','lrmer_co2_p','lrmer_ch4_p','lrmer_n2o_p','lrmer_co2e_c','lrmer_co2e_p','lrmer_co2e',\
        #                                                                                         'generation','nuclear_MWh','coal_MWh','coal-ccs_MWh','o-g-s_MWh','gas-cc_MWh','gas-cc-ccs_MWh','gas-ct_MWh','hydro_MWh','geothermal_MWh',\
        #                                                                                         'biomass_MWh','beccs_MWh','wind-ons_MWh','wind-ofs_MWh','csp_MWh','upv_MWh','distpv_MWh','phs_MWh','battery_MWh','canada_MWh'])

        # cambium_data = cambium_data.reset_index().rename(columns = {'index':'Interval','lrmer_co2_c':'LRMER CO2 combustion (kg-CO2/MWh)','lrmer_ch4_c':'LRMER CH4 combustion (g-CH4/MWh)','lrmer_n2o_c':'LRMER N2O combustion (g-N2O/MWh)',\
        #                                             'lrmer_co2_p':'LRMER CO2 production (kg-CO2/MWh)','lrmer_ch4_p':'LRMER CH4 production (g-CH4/MWh)','lrmer_n2o_p':'LRMER N2O production (g-N2O/MWh)','lrmer_co2e_c':'LRMER CO2 equiv. combustion (kg-CO2e/MWh)',\
        #                                             'lrmer_co2e_p':'LRMER CO2 equiv. production (kg-CO2e/MWh)','lrmer_co2e':'LRMER CO2 equiv. total (kg-CO2e/MWh)'})

        cambium_data = pd.read_csv(cambiumdata_filepath,index_col = None,header = 5,usecols = ['aer_gen_co2e','aer_load_co2e','lrmer_co2e',\
                                                                                                'generation','nuclear_MWh','coal_MWh','coal-ccs_MWh','o-g-s_MWh','gas-cc_MWh','gas-cc-ccs_MWh','gas-ct_MWh','hydro_MWh','geothermal_MWh',\
                                                                                                'biomass_MWh','beccs_MWh','wind-ons_MWh','wind-ofs_MWh','csp_MWh','upv_MWh','distpv_MWh','phs_MWh','battery_MWh','canada_MWh'])

        cambium_data = cambium_data.reset_index().rename(columns = {'index':'Interval'})

        cambium_data['Interval']=cambium_data['Interval']+1
        cambium_data = cambium_data.set_index('Interval')

        # Calculate precombustion and combustion emissions using GREET assumptions
        cambium_data['total precombustion emissions (kg-CO2)'] = 0*cambium_data['generation']
        cambium_data['total combustion emissions (kg-CO2)'] = 0*cambium_data['generation']
        for fossil_technology in emitting_technologies:
            cambium_data['total precombustion emissions (kg-CO2)'] = cambium_data['total precombustion emissions (kg-CO2)']+greet_ei.loc[fossil_technology,'Pre-combustion (kg CO2e/MWh)']*cambium_data[fossil_technology+'_MWh']
            cambium_data['total combustion emissions (kg-CO2)'] = cambium_data['total combustion emissions (kg-CO2)']+greet_ei.loc[fossil_technology,'Combustion (kg CO2e/MWh)']*cambium_data[fossil_technology+'_MWh']

        cambium_data['total average precombustion emissions (kg-CO2/MWhe)'] = cambium_data['total precombustion emissions (kg-CO2)']/cambium_data['generation']
        cambium_data['total average combustion emissions (kg-CO2/MWhe)'] = cambium_data['total combustion emissions (kg-CO2)']/cambium_data['generation']
        cambium_data['total average grid emissions (kg-CO2/MWhe)'] = (cambium_data['total average precombustion emissions (kg-CO2/MWhe)']+cambium_data['total average combustion emissions (kg-CO2/MWhe)'])

        # Compare to cambium
        cambium_data['greet-cambium average emission difference (kg-CO2/MWhe)'] = cambium_data['total average grid emissions (kg-CO2/MWhe)'] -cambium_data['aer_gen_co2e']
        cambium_data['greet-cambium average emission difference (%)'] = (cambium_data['total average grid emissions (kg-CO2/MWhe)'] -cambium_data['aer_gen_co2e'])/cambium_data['aer_gen_co2e']*100

        # Calculate hourly grid emissions factors of interest. If we want to use different GWPs, we can do that here. The Grid Import is an hourly data i.e., in MWh
        # cambium_data['Total grid emissions (kg-CO2e)'] = energy_from_grid_df['Energy from the grid (kWh)'] * cambium_data['LRMER CO2 equiv. total (kg-CO2e/MWh)'] / 1000
        # cambium_data['Scope 2 (combustion) grid emissions (kg-CO2e)'] = energy_from_grid_df['Energy from the grid (kWh)']  * cambium_data['LRMER CO2 equiv. combustion (kg-CO2e/MWh)'] / 1000
        # cambium_data['Scope 3 (production) grid emissions (kg-CO2e)'] = energy_from_grid_df['Energy from the grid (kWh)']  * cambium_data['LRMER CO2 equiv. production (kg-CO2e/MWh)'] / 1000

        # Calculate hourly grid emissions factors of interestusing GREET assumptions. The Grid Import is an hourly data i.e., in MWh
        cambium_data['Total grid emissions (kg-CO2e)'] = energy_from_grid_df['Energy from the grid (kWh)'] * cambium_data['total average grid emissions (kg-CO2/MWhe)'] / 1000
        cambium_data['Scope 2 (combustion) grid emissions (kg-CO2e)'] = energy_from_grid_df['Energy from the grid (kWh)']  * cambium_data['total average combustion emissions (kg-CO2/MWhe)'] / 1000
        cambium_data['Scope 3 (production) grid emissions (kg-CO2e)'] = energy_from_grid_df['Energy from the grid (kWh)']  * cambium_data['total average precombustion emissions (kg-CO2/MWhe)']/ 1000

        # Sum total emissions
        scope2_grid_emissions_sum = cambium_data['Scope 2 (combustion) grid emissions (kg-CO2e)'].sum()*kg_to_MT_conv
        scope3_grid_emissions_sum = cambium_data['Scope 3 (production) grid emissions (kg-CO2e)'].sum()*kg_to_MT_conv
        #scope3_ren_sum            = energy_from_renewables_df['Energy from renewables (kWh)'].sum()/1000 # MWh
        scope3_ren_sum            = energy_from_renewables_df['Energy from renewables (kWh)'].sum()/1000 # MWh
        #h2prod_sum = np.sum(hydrogen_production_while_running)*system_life*kg_to_MT_conv
    #    h2prod_grid_frac = cambium_data['Grid Import (MW)'].sum() / cambium_data['Electrolyzer Power (MW)'].sum()
        h2prod_sum=H2_Results['hydrogen_annual_output']*kg_to_MT_conv


        if grid_connection_scenario == 'hybrid-grid' :
            # Calculate grid-connected electrolysis emissions/ future cases should reflect targeted electrolyzer electricity usage
            electrolysis_Scope3_EI =  scope3_grid_emissions_sum/h2prod_sum # + (wind_capex_EI + solar_pv_capex_EI + battery_EI) * (scope3_ren_sum/h2prod_sum) * g_to_kg_conv + ely_stack_capex_EI # kg CO2e/kg H2
            electrolysis_Scope2_EI =  scope2_grid_emissions_sum/h2prod_sum
            electrolysis_Scope1_EI = 0
            electrolysis_total_EI  = electrolysis_Scope1_EI + electrolysis_Scope2_EI + electrolysis_Scope3_EI
            electrolysis_total_EI_policy_grid = electrolysis_total_EI # - (wind_capex_EI + solar_pv_capex_EI + battery_EI) * (scope3_ren_sum/h2prod_sum)  * g_to_kg_conv
            electrolysis_total_EI_policy_offgrid = 0 #(wind_capex_EI + solar_pv_capex_EI + battery_EI) * (scope3_ren_sum/h2prod_sum)  * g_to_kg_conv + ely_stack_capex_EI
        elif grid_connection_scenario == 'grid-only':
            # Calculate grid-connected electrolysis emissions
            electrolysis_Scope3_EI = scope3_grid_emissions_sum/h2prod_sum # + ely_stack_capex_EI # kg CO2e/kg H2
            electrolysis_Scope2_EI = scope2_grid_emissions_sum/h2prod_sum
            electrolysis_Scope1_EI = 0
            electrolysis_total_EI = electrolysis_Scope1_EI + electrolysis_Scope2_EI + electrolysis_Scope3_EI
            electrolysis_total_EI_policy_grid = electrolysis_total_EI
            electrolysis_total_EI_policy_offgrid = 0
        elif grid_connection_scenario == 'off-grid':
            # Calculate renewable only electrolysis emissions
            electrolysis_Scope3_EI = 0#(wind_capex_EI + solar_pv_capex_EI + battery_EI) * (scope3_ren_sum/h2prod_sum)  * g_to_kg_conv + ely_stack_capex_EI # kg CO2e/kg H2
            electrolysis_Scope2_EI = 0
            electrolysis_Scope1_EI = 0
            electrolysis_total_EI = electrolysis_Scope1_EI + electrolysis_Scope2_EI + electrolysis_Scope3_EI
            electrolysis_total_EI_policy_offgrid = electrolysis_total_EI
            electrolysis_total_EI_policy_grid = 0

        emission_intensity_grid.append(electrolysis_total_EI_policy_grid)
        emission_intensity_offgrid.append(electrolysis_total_EI_policy_offgrid)
        
    emission_intensities_df = pd.DataFrame({'Year':years,'Grid EI (kg CO2e/kg H2)':emission_intensity_grid,'Off-grid EI (kg CO2e/kg H2)':emission_intensity_offgrid})

    # Interpolate results
    endofincentives_year = cambium_year + H2_PTC_duration

    grid_EI_interpolated = {}
    offgrid_EI_interpolated = {}
    for year in range(cambium_year,endofincentives_year):
        if year <= max(emission_intensities_df['Year']):
            grid_EI_interpolated[year]=np.interp(year,emission_intensities_df['Year'],emission_intensities_df['Grid EI (kg CO2e/kg H2)'])
            offgrid_EI_interpolated[year]=np.interp(year,emission_intensities_df['Year'],emission_intensities_df['Off-grid EI (kg CO2e/kg H2)'])
        else:
            grid_EI_interpolated[year]=emission_intensities_df['Grid EI (kg CO2e/kg H2)'].values[-1:][0]
            offgrid_EI_interpolated[year]=emission_intensities_df['Off-grid EI (kg CO2e/kg H2)'].values[-1:][0]

    return(grid_EI_interpolated,offgrid_EI_interpolated)


