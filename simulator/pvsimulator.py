import datetime as dt
import pandas as pd
import pvlib.atmosphere as atmosphere
import pvlib.irradiance as irradiance
import pvlib.pvsystem as pvsystem
import pvlib.solarposition as solarposition

from pvlib.location import Location

_sandia_modules = pvsystem.retrieve_sam('SandiaMod')
_cec_inverters = pvsystem.retrieve_sam('cecinverter')
_sandia_module = _sandia_modules['Silevo_Triex_U300_Black__2014_']
_cec_inverter = _cec_inverters['ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_']
_munich_location = Location(48.3, 11.8, 'CET', 447, 'Munich')
_module_count = 20


def get_perfect_voltage_for_a_day(start, freq):
    """This method is used to build a pandas serie with voltage values.
    This serie has DateTime index and contains a value for every "freq"
    seconds during 24 hours starting from "start" date.
    There are several assumptions:
    1. Location is Munich
    2. A battery is pointing to the south, amount of blocks is 20
    3. Sandia Module database is used
    4. pvlib library is heavily used

    :param start: datetime. First timestamp in result series
    :param freq: str. How often voltage should be sampled
    :return: voltage : Series
    """
    surface_tilt = _munich_location.latitude
    surface_azimuth = 180  # pointing south
    date_range = pd.date_range(start=start,
                               end=start + dt.timedelta(
                                   hours=23, minutes=59, seconds=59),
                               freq=freq, tz=_munich_location.tz)

    clearsky_estimations = _munich_location.get_clearsky(date_range)
    dni_extra = irradiance.extraradiation(date_range)
    solar_position = solarposition.get_solarposition(
        date_range, _munich_location.latitude, _munich_location.longitude)
    airmass = atmosphere.relativeairmass(solar_position['apparent_zenith'])
    pressure = atmosphere.alt2pres(_munich_location.altitude)
    am_abs = atmosphere.absoluteairmass(airmass, pressure)

    total_irrad = irradiance.total_irrad(surface_tilt,
                                         surface_azimuth,
                                         solar_position['apparent_zenith'],
                                         solar_position['azimuth'],
                                         clearsky_estimations['dni'],
                                         clearsky_estimations['ghi'],
                                         clearsky_estimations['dhi'],
                                         dni_extra=dni_extra,
                                         model='haydavies')

    temps = pvsystem.sapm_celltemp(total_irrad['poa_global'], 0, 15)
    aoi = irradiance.aoi(surface_tilt, surface_azimuth,
                         solar_position['apparent_zenith'],
                         solar_position['azimuth'])
    # add 0.0001 to avoid np.log(0) and warnings about that
    effective_irradiance = pvsystem.sapm_effective_irradiance(
        total_irrad['poa_direct'], total_irrad['poa_diffuse'], am_abs,
        aoi, _sandia_module) + 0.0001
    sapm = pvsystem.sapm(effective_irradiance, temps['temp_cell'],
                         _sandia_module)

    return sapm['p_mp'] * _module_count
