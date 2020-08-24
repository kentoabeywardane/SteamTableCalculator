import numpy as np
import pandas as pd

SatWatTemp = pd.DataFrame()
SatWatPres = pd.DataFrame()
SupWat = pd.DataFrame()
CompWat = pd.DataFrame()


def out(df, sheet):
    excel = pd.read_excel('steam tables.xlsx', sheet_name=sheet)
    for column in excel.columns:
        df[column] = excel[column].apply(lambda x: x.split()).explode().reset_index().drop('index', axis=1).squeeze()
    for column in df.columns:
        df[column] = df[column].apply(lambda x: float(x))
    df.set_index([df.columns[0], df.columns[1]], inplace=True)
    if 'Sat Liq vf' in df.columns:
        df['Sat Liq vf'] = df['Sat Liq vf'].div(1000)
    # return df


sheetNames = ['Saturated Water (Temp Table)', 'Saturated Water (Pres Table)', 'Superheated Water', 'Compressed Water']
out(SatWatTemp, sheetNames[0])
out(SatWatPres, sheetNames[1])
out(SupWat, sheetNames[2])
out(CompWat, sheetNames[3])

# noinspection SpellCheckingInspection
SatWat = pd.concat([SatWatTemp.reset_index(), SatWatPres.reset_index()[['Temp', 'Pres', 'Sat Liq vf',
                                                                        'Sat Vap vg', 'Sat Liq uf', 'Sat Vap ug',
                                                                        'Sat Liq hf', 'Evap hfg', 'Sat Vap hg',
                                                                        'Sat Liq sf', 'Sat Vap sg']]])
SatWat = SatWat.sort_values(by=['Temp']).drop_duplicates(subset=['Pres'])
SatWat = SatWat.set_index([SatWat.columns[0], SatWat.columns[1]])

CompWat['v'] = CompWat['v'].div(1000)

#    Copy and Paste From Here last updated: 8/23
#   ------------------------------------------------------------------------------------------
#   Superheated and Compressed Values


class NonSat:
    def __init__(self, df):
        self.df = df
        self.pressure_list = np.unique(df.index.get_level_values(0))

    def where_pressure(self, p):
        """Determines whether pressure is on table."""
        if p in self.pressure_list:
            return self.pressure_list.tolist().index(p)  # returns index (int) of pressure table
        elif p < self.pressure_list[0] or p > self.pressure_list[-1]:
            return f'Pressure must be between {self.pressure_list[0]} - {self.pressure_list[-1]} bar.'  # pressure not in pressure table
        elif self.pressure_list[0] < p < self.pressure_list[-1]:
            pres_position = np.searchsorted(self.pressure_list, p)
            return pres_position  # returns where pressure is between table

    def interpolation_instruction(self, p):
        """Gives instructions on what path to follow based on where pressure is on table."""
        if type(self.where_pressure(p)) is int:
            return 'on table'
        elif type(self.where_pressure(p)) is np.int64:
            return 'between table'
        else:
            return self.where_pressure(p)

    def interpolate_temp(self, p, t):
        """Simple interpolation given a pressure on the table and a random temperature.
            Returns dictionary with all elements from table."""
        temp_df = self.df.xs(p, level=0).T
        position = np.searchsorted(temp_df.keys(), t)
        x = (t - temp_df.keys()[position - 1]) / (temp_df.keys()[position] - temp_df.keys()[position - 1])
        list_df = self.df.xs(p, level=0)
        dictionary = {}
        for names in self.df.xs(p, level=0).columns:
            y = x * (list_df[names].values[position] - list_df[names].values[position - 1]) + list_df[names].values[
                position - 1]
            dictionary.update({names: y})
        return dictionary

    def interpolate_temp_from_pressure(self, p, z, column):
        """Simple interpolation given a pressure on the table and a random element.
            Returns temperature for the corresponding element."""
        list_df = self.df.xs(p, level=0)[column]
        position = np.searchsorted(list_df.values, z)
        x = (z - list_df.values[position - 1]) / (list_df.values[position] - list_df.values[position - 1])
        y = x * (list_df.keys()[position] - list_df.keys()[position - 1]) + list_df.keys()[position - 1]
        return y

    def flow_to_interpolate_from_pressure(self, p, z, column):
        """Gives instructions for how to execute code given a pressure on the table and a random element."""
        if z > self.df.xs(p, level=0)[column].values[-1]:
            return f'Inputted value ({z}) too large'
        elif z < self.df.xs(p, level=0)[column].values[0]:
            return f'Inputted value ({z}) too small'
        elif z == self.df.xs(p, level=0)[column].values[-1]:
            return self.df.xs(p, level=0)[column].keys()[-1]
        elif z == self.df.xs(p, level=0)[column].values[0]:
            return self.df.xs(p, level=0)[column].keys()[0]
        else:
            return self.interpolate_temp_from_pressure(p, z, column)

    def pretty_return(self, p, z, column):
        """Code wrapper for efficient output."""
        output = self.flow_to_interpolate_from_pressure(p, z, column)
        if type(output) is np.float64:
            return [output, self.interpolate_temp(p, output)]
        else:
            return output

    @staticmethod
    def output_final_dict(dh, dl, xp):
        """Returns final interpolated values for each element in table using pressure position."""
        fd = {}
        for k in dh:
            z = xp * (dh.get(k) - dl.get(k)) + dl.get(k)
            fd.update({k: z})
        return fd

    def triple_interpolation_variables(self, p):
        """Establishes variables used in triple interpolation."""
        pres_position = np.searchsorted(self.pressure_list, p)
        x_pres = (p - self.pressure_list[pres_position - 1]) / (self.pressure_list[pres_position] - self.pressure_list[pres_position - 1])
        temp_df_high = self.df.xs(self.pressure_list[pres_position], level=0).T
        temp_df_low = self.df.xs(self.pressure_list[pres_position - 1], level=0).T
        return [pres_position, x_pres, temp_df_high, temp_df_low]

    def triple_interpolation_t_element(self, section, pres_position, t):
        """Element of triple interpolation when temperature is given.
            Returns dictionary with each interpolated element using temperature position."""
        column_names = self.df.xs(self.pressure_list[pres_position], level=0).columns
        interp_dictionary = {}
        t_pos = np.searchsorted(section.keys(), t)
        x = (t - section.keys()[t_pos - 1]) / (section.keys()[t_pos] - section.keys()[t_pos - 1])
        for names in column_names:
            y = x * (section.T[names].values[t_pos] - section.T[names].values[t_pos - 1]) + section.T[names].values[
                t_pos - 1]
            interp_dictionary.update({names: y})
        return interp_dictionary

    def triple_interpolation_t(self, p, t):
        """Triple interpolation given temperature flow code.
            Returns dictionary of properly interpolated elements."""
        [pres_position, x_pres, temp_df_high, temp_df_low] = self.triple_interpolation_variables(p)

        if temp_df_high.keys()[0] < t < temp_df_high.keys()[-1] and temp_df_low.keys()[0] < t < temp_df_low.keys()[-1]:
            if t in temp_df_high.keys() and t in temp_df_low.keys():
                d_high = temp_df_high[t].to_dict()
                d_low = temp_df_low[t].to_dict()
                return self.output_final_dict(d_high, d_low, x_pres)

            elif t in temp_df_high.keys() and t not in temp_df_low.keys():
                d_high = temp_df_high[t].to_dict()
                d_low = self.triple_interpolation_t_element(temp_df_low, pres_position, t)
                return self.output_final_dict(d_high, d_low, x_pres)

            elif t not in temp_df_high.keys() and t in temp_df_low.keys():
                d_high = self.triple_interpolation_t_element(temp_df_high, pres_position, t)
                d_low = temp_df_low[t].to_dict()
                return self.output_final_dict(d_high, d_low, x_pres)

            else:
                d_high = self.triple_interpolation_t_element(temp_df_high, pres_position, t)
                d_low = self.triple_interpolation_t_element(temp_df_low, pres_position, t)
                return self.output_final_dict(d_high, d_low, x_pres)

        elif t < temp_df_high.keys()[0] or t < temp_df_low.keys()[0]:
            return f'Temperature must be higher than {max([temp_df_high.keys()[0], temp_df_low.keys()[0]])} C'

        elif t > temp_df_high.keys()[-1] or t > temp_df_low.keys()[-1]:
            return f'Temperature must be lower than {min([temp_df_high.keys()[-1], temp_df_low.keys()[-1]])} C'

        elif t == max([temp_df_high.keys()[0], temp_df_low.keys()[0]]):
            max_t_pos = np.argmax([temp_df_high.keys()[0], temp_df_low.keys()[0]])
            if max_t_pos == 0:
                d_high = temp_df_high[t].to_dict()
                d_low = self.triple_interpolation_t_element(temp_df_low, pres_position, t)
                return self.output_final_dict(d_high, d_low, x_pres)

            elif max_t_pos == 1:
                d_high = self.triple_interpolation_t_element(temp_df_high, pres_position, t)
                d_low = temp_df_low[t].to_dict()
                return self.output_final_dict(d_high, d_low, x_pres)

        elif t == min([temp_df_high.keys()[-1], temp_df_low.keys()[-1]]):
            min_t_pos = np.argmin([temp_df_high.keys()[-1], temp_df_low.keys()[-1]])
            if min_t_pos == 0:
                d_high = temp_df_high[t].to_dict()
                d_low = self.triple_interpolation_t_element(temp_df_low, pres_position, t)
                return self.output_final_dict(d_high, d_low, x_pres)

            elif min_t_pos == 1:
                d_high = self.triple_interpolation_t_element(temp_df_high, pres_position, t)
                d_low = temp_df_low[t].to_dict()
                return self.output_final_dict(d_high, d_low, x_pres)

    def triple_interpolation_z_element(self, temp_df, zdf, z, pres_position, inout):
        """Element of triple interpolation when an elemental value is given.
            Depending on whether the elemental value appears on a table, it follows a flow where both instances
            return its corresponding temperature and
            dictionary with each interpolated element."""
        if inout == 'in':
            z_pos = np.where(zdf.values == z)[0][0]
            y = temp_df.keys()[z_pos]
            return [y, temp_df[y].to_dict()]
        elif inout == 'out':
            z_pos = np.searchsorted(zdf.values, z)
            x = (z - zdf.values[z_pos - 1]) / (zdf.values[z_pos] - zdf.values[z_pos - 1])
            y = x * (zdf.keys()[z_pos] - zdf.keys()[z_pos - 1]) + zdf.keys()[z_pos - 1]
            return [y, self.triple_interpolation_t_element(temp_df, pres_position, y)]

    def triple_interpolation_z(self, p, z, column):
        """Triple interpolation given an elemental value; flow code.
            Returns list with interpolated temperature and dictionary of properly interpolated elements."""
        [pres_position, x_pres, temp_df_high, temp_df_low] = self.triple_interpolation_variables(p)
        zdf_high = self.df.xs(self.pressure_list[pres_position], level=0)[column]
        zdf_low = self.df.xs(self.pressure_list[pres_position - 1], level=0)[column]

        column_units = {'v': 'm3/kg', 'u': 'kJ/kg', 'h': 'kJ/kg', 's': 'kJ/kg-K'}

        if zdf_high.values[0] < z < zdf_high.values[-1] and zdf_low.values[0] < z < zdf_low.values[-1]:

            if z in zdf_high.values and z in zdf_low.values:
                [y_high, d_high] = self.triple_interpolation_z_element(temp_df_high, zdf_high, z, pres_position, 'in')
                [y_low, d_low] = self.triple_interpolation_z_element(temp_df_low, zdf_low, z, pres_position, 'in')
                final_t = x_pres * (y_high - y_low) + y_low
                return [final_t, self.output_final_dict(d_high, d_low, x_pres)]

            elif z in zdf_high.values and z not in zdf_low.values:
                [y_high, d_high] = self.triple_interpolation_z_element(temp_df_high, zdf_high, z, pres_position, 'in')
                [y_low, d_low] = self.triple_interpolation_z_element(temp_df_low, zdf_low, z, pres_position, 'out')
                final_t = x_pres * (y_high - y_low) + y_low
                return [final_t, self.output_final_dict(d_high, d_low, x_pres)]

            elif z not in zdf_high.values and z in zdf_low.values:
                [y_high, d_high] = self.triple_interpolation_z_element(temp_df_high, zdf_high, z, pres_position, 'out')
                [y_low, d_low] = self.triple_interpolation_z_element(temp_df_low, zdf_low, z, pres_position, 'in')
                final_t = x_pres * (y_high - y_low) + y_low
                return [final_t, self.output_final_dict(d_high, d_low, x_pres)]

            else:  # z not in either
                [y_high, d_high] = self.triple_interpolation_z_element(temp_df_high, zdf_high, z, pres_position, 'out')
                [y_low, d_low] = self.triple_interpolation_z_element(temp_df_low, zdf_low, z, pres_position, 'out')
                final_t = x_pres * (y_high - y_low) + y_low
                return [final_t, self.output_final_dict(d_high, d_low, x_pres)]

        elif z < zdf_high.values[0] or z < zdf_low.values[0]:
            return f'Inputted value ({column}) must be higher than {max([zdf_high.values[0], zdf_low.values[0]])} {column_units[column]}'

        elif z > zdf_high.values[-1] or z > zdf_low.values[-1]:
            return f'Inputted value ({column}) must be lower than {min([zdf_high.values[-1], zdf_low.values[-1]])} {column_units[column]}'

        elif z == max([zdf_high.values[0], zdf_low.values[0]]):
            max_z_pos = np.argmax([zdf_high.values[0], zdf_low.values[0]])
            if max_z_pos == 0:
                y_high = temp_df_high.keys()[0]
                d_high = temp_df_high[y_high].to_dict()
                [y_low, d_low] = self.triple_interpolation_z_element(temp_df_low, zdf_low, z, pres_position, 'out')
                final_t = x_pres * (y_high - y_low) + y_low
                return [final_t, self.output_final_dict(d_high, d_low, x_pres)]

            elif max_z_pos == 1:
                [y_high, d_high] = self.triple_interpolation_z_element(temp_df_high, zdf_high, z, pres_position, 'out')
                y_low = temp_df_low.keys()[0]
                d_low = temp_df_low[y_low].to_dict()
                final_t = x_pres * (y_high - y_low) + y_low
                return [final_t, self.output_final_dict(d_high, d_low, x_pres)]

        elif z == min([zdf_high.values[-1], zdf_low.values[-1]]):
            min_z_pos = np.argmin([zdf_high.values[-1], zdf_low.values[-1]])
            if min_z_pos == 0:
                y_high = temp_df_high.keys()[-1]
                d_high = temp_df_high[y_high].to_dict()
                [y_low, d_low] = self.triple_interpolation_z_element(temp_df_low, zdf_low, z, pres_position, 'out')
                final_t = x_pres * (y_high - y_low) + y_low
                return [final_t, self.output_final_dict(d_high, d_low, x_pres)]

            if min_z_pos == 1:
                [y_high, d_high] = self.triple_interpolation_z_element(temp_df_high, zdf_high, z, pres_position, 'out')
                y_low = temp_df_low.keys()[-1]
                d_low = temp_df_low[y_low].to_dict()
                final_t = x_pres * (y_high - y_low) + y_low
                return [final_t, self.output_final_dict(d_high, d_low, x_pres)]

    def outer_dome(self, p=None, t=None, v=None, u=None, h=None, s=None):
        """Flow instructions for reading a compressed liquid / superheated water vapor table."""
        if [p, t, v, u, h, s].count(None) != 4:
            return 'Enter exactly 2 values'

        elif p is None:  # maybe temporary?
            return 'Need a pressure'

        elif p is not None:
            if self.interpolation_instruction(p) == 'on table':
                if t is not None:
                    if self.df.xs(p, level=0).T.keys().max() >= t >= self.df.xs(p, level=0).T.keys().min():
                        if t in self.df.xs(p, level=0).T:
                            return dict(self.df.xs((p, t)))
                        else:
                            return self.interpolate_temp(p, t)
                    else:
                        return f'Temperature must be within the range of {self.df.xs(p, level=0).T.keys().min()} - {self.df.xs(p, level=0).T.keys().max()} C'

                elif v is not None:
                    return self.pretty_return(p, v, 'v')

                elif u is not None:
                    return self.pretty_return(p, u, 'u')

                elif h is not None:
                    return self.pretty_return(p, h, 'h')

                elif s is not None:
                    return self.pretty_return(p, s, 's')

            elif self.interpolation_instruction(p) == f'Pressure must be between {self.pressure_list[0]} - {self.pressure_list[-1]} bar.':
                return self.interpolation_instruction(p)

            elif self.interpolation_instruction(p) == 'between table':
                if t is not None:
                    return self.triple_interpolation_t(p, t)

                if v is not None:
                    return self.triple_interpolation_z(p, v, 'v')

                if u is not None:
                    return self.triple_interpolation_z(p, u, 'u')

                if h is not None:
                    return self.triple_interpolation_z(p, h, 'h')

                if s is not None:
                    return self.triple_interpolation_z(p, s, 's')


#   Saturated Values
#   ----------------------------------------- updated 8/23
def return_row(element, column):
    pos = np.where(column == element)[0][0]
    el_dict = SatWat.xs(SatWat.index[pos]).to_dict()
    f_dict = {}
    names = SatWat.index.names
    f_dict.update({names[0]: SatWat.index[pos][0], names[1]: SatWat.index[pos][1]})
    f_dict.update(el_dict)
    return f_dict


class InterpolateRow:
    def __init__(self, ascending_lst_values, ind, element):
        self.lst = ascending_lst_values
        self.ind = ind
        self.elem = element
        self.z_pos = np.searchsorted(self.lst, self.elem)
        self.x = (self.elem - self.lst[self.z_pos - 1]) / (self.lst[self.z_pos] - self.lst[self.z_pos - 1])
        self.t_val = (self.x * (
                self.ind.get_level_values(0)[self.z_pos] - self.ind.get_level_values(0)[self.z_pos - 1]) +
                      self.ind.get_level_values(0)[self.z_pos - 1])
        self.p_val = (self.x * (
                self.ind.get_level_values(1)[self.z_pos] - self.ind.get_level_values(1)[self.z_pos - 1]) +
                      self.ind.get_level_values(1)[self.z_pos - 1])
        self.in_dict = {SatWat.index.names[0]: self.t_val, SatWat.index.names[1]: self.p_val}
        self.empty_dict = {}
        self.names = SatWat.columns

    def simple(self):
        for col in self.names:
            el_val = self.x * (SatWat[col].values[self.z_pos] - SatWat[col].values[self.z_pos - 1]) + \
                     SatWat[col].values[self.z_pos - 1]
            self.empty_dict.update({col: el_val})
        self.in_dict.update(self.empty_dict)
        return self.in_dict

    def complx(self):
        for col in self.names:
            if col == 'Sat Vap ug':
                sw_rev = SatWat['Sat Vap ug'].values[::-1]
                el_val = self.x * (sw_rev[self.z_pos] - sw_rev[self.z_pos - 1]) + sw_rev[self.z_pos - 1]
                self.empty_dict.update({col: el_val})
            elif col == 'Sat Vap hg':
                sw_rev = SatWat['Sat Vap hg'].values[::-1]
                el_val = self.x * (sw_rev[self.z_pos] - sw_rev[self.z_pos - 1]) + sw_rev[self.z_pos - 1]
                self.empty_dict.update({col: el_val})
            elif SatWat[col].values[0] < SatWat[col].values[-1]:  # ascending must be reversed
                el_val = self.x * (SatWat[col].sort_values(ascending=False).values[self.z_pos] -
                                   SatWat[col].sort_values(ascending=False).values[self.z_pos - 1]) + \
                         SatWat[col].sort_values(ascending=False).values[self.z_pos - 1]
                self.empty_dict.update({col: el_val})
            elif SatWat[col].values[0] > SatWat[col].values[-1]:
                el_val = self.x * (SatWat[col].sort_values(ascending=True).values[self.z_pos] -
                                   SatWat[col].sort_values(ascending=True).values[self.z_pos - 1]) + \
                         SatWat[col].sort_values(ascending=True).values[self.z_pos - 1]
                self.empty_dict.update({col: el_val})
        self.in_dict.update(self.empty_dict)
        return self.in_dict


class QualityCalculation:
    @staticmethod
    def non_pt(z, column):
        if SatWat[column].values[0] < SatWat[column].values[-1]:  # already ascending: only happens with f columns
            sw_ascend = SatWat[column].sort_values().values
            sw_index = SatWat[column].index
            if pd.Series.between(z, sw_ascend[0], sw_ascend[-1]):
                if z in SatWat[column].values:
                    return return_row(z, SatWat[column].values)
                else:
                    return InterpolateRow(sw_ascend, sw_index, z).simple()
            else:
                f'{z} is not in range for {column}.\nMust be within range: {SatWat[column].values[0]}-{SatWat[column].values[-1]}.'

        elif SatWat[column].values[0] > SatWat[column].values[-1]:  # descending: only happens with vg and sg
            sw_ascend = SatWat[column].sort_values().values
            sw_index = SatWat[column].sort_values().index
            if pd.Series.between(z, sw_ascend[0], sw_ascend[-1]):
                if z in SatWat[column].values:
                    return return_row(z, SatWat[column].values)
                else:
                    return InterpolateRow(sw_ascend, sw_index, z).complx()
            else:
                f'{z} is not in range for {column}.\nMust be within range: {SatWat[column].values[-1]}-{SatWat[column].values[0]}.'

    @staticmethod
    def d_pop(dictionary, line):
        for x in list(dictionary.keys()):
            if f'{line}' in x:
                dictionary.pop(x)
            else:
                pass
        return dictionary

    @staticmethod
    def values(dictionary, q):
        new_labels = [list(dictionary.keys())[0], list(dictionary.keys())[1], 'v', 'u', 'h', 's', 'quality']
        d_values = list(dictionary.values())
        v_val = q * (d_values[3] - d_values[2]) + d_values[2]
        u_val = q * (d_values[5] - d_values[4]) + d_values[4]
        h_val = q * (d_values[7]) + d_values[6]
        s_val = q * (d_values[10] - d_values[9]) + d_values[9]
        new_values = [d_values[0], d_values[1], v_val, u_val, h_val, s_val, q]
        return dict(zip(new_labels, new_values))

    @staticmethod
    def pt(ptx, q, index):
        if q == 0:  # liq line
            if ptx in index:
                d = return_row(ptx, index)
                return QualityCalculation().d_pop(d, 'g')
            elif index[0] < ptx < index[-1]:
                d = InterpolateRow(index, SatWat.index, ptx).simple()
                return QualityCalculation().d_pop(d, 'g')
            else:
                return f'{ptx} value must be within range of {index[0]} - {index[-1]}'
        elif q == 1:  # vap line
            if ptx in index:
                d = return_row(ptx, index)
                return QualityCalculation().d_pop(d, 'f')
            elif index[0] < ptx < index[-1]:
                d = InterpolateRow(index, SatWat.index, ptx).simple()
                return QualityCalculation().d_pop(d, 'f')
            else:
                return f'{ptx} value must be within range of {index[0]} - {index[-1]}'
        else:
            if ptx in index:
                d = return_row(ptx, index)
                return QualityCalculation().values(d, q)
            elif index[0] < ptx < index[-1]:
                d = InterpolateRow(index, SatWat.index, ptx).simple()
                return QualityCalculation().values(d, q)
            else:
                return f'{ptx} value must be within range of {index[0]} - {index[-1]}'


def saturated(p=None, t=None, v=None, u=None, h=None, s=None, quality=None):
    if [p, t].count(None) == 2:  # expect 1 of v/u/h/s and quality of 0 or 1
        if [v, u, h, s].count(None) != 3:
            return 'Without a pressure or temperature,\nonly enter 1 value out of v, u, h, and s WITH a quality of 0 or 1.\n(signifies value on the saturated liq/vap line)'
        else:
            if quality == 1:  # interpolate using vapor line
                if v is not None:
                    return QualityCalculation().non_pt(v, 'Sat Vap vg')
                elif u is not None:
                    return 'Cannot interpolate off of vapor line only using internal energy and quality.'
                elif h is not None:
                    return 'Cannot interpolate off of vapor line only using enthalpy and quality.'
                elif s is not None:
                    return QualityCalculation().non_pt(s, 'Sat Vap sg')

            elif quality == 0:
                if v is not None:
                    return QualityCalculation().non_pt(v, 'Sat Liq vf')
                elif u is not None:
                    return QualityCalculation().non_pt(u, 'Sat Liq uf')
                elif h is not None:
                    return QualityCalculation().non_pt(h, 'Sat Liq hf')
                elif s is not None:
                    return QualityCalculation().non_pt(s, 'Sat Liq sf')

            elif 0 < quality < 1:
                return 'Without a pressure or temperature,\nonly enter 1 value out of v, u, h, and s WITH a quality of 0 or 1.\n(signifies value on the saturated liq/vap line)'
            else:
                return 'Without a pressure or temperature,\nonly enter 1 value out of v, u, h, and s WITH a quality of 0 or 1.\n(signifies value on the saturated liq/vap line)'

    elif [p, t].count(None) == 1:
        if p is not None:
            if quality is not None:  # p and q
                if 0 <= quality <= 1:
                    if [v, u, h, s].count(None) == 4:
                        return QualityCalculation().pt(p, quality, SatWat.index.get_level_values(1))
                    else:
                        return 'Given a pressure, including quality and another value is redundant.\nFor this, choose one.'
                else:
                    return 'Quality must be between 0 and 1.'

            elif quality is None:
                if [v, u, h, s].count(None) == 4:  # only p
                    if p in SatWat.index.get_level_values(1):
                        return return_row(p, SatWat.index.get_level_values(1))
                    elif SatWat.index.get_level_values(1)[0] < p < SatWat.index.get_level_values(1)[-1]:
                        return InterpolateRow(SatWat.index.get_level_values(1), SatWat.index, p).simple()
                    else:
                        return 'Pressure not in saturated range'

                elif [v, u, h, s].count(None) == 3:  # p and v/u/h/s
                    if SatWat.index.get_level_values(1)[0] <= p < SatWat.index.get_level_values(1)[-1]:
                        if v is not None:
                            lst = list(saturated(p=p).values())
                            q = (v - lst[2]) / (lst[3] - lst[2])
                            return saturated(p=p, quality=q)
                        elif u is not None:
                            lst = list(saturated(p=p).values())
                            q = (u - lst[4]) / (lst[5] - lst[4])
                            return saturated(p=p, quality=q)
                        elif h is not None:
                            lst = list(saturated(p=p).values())
                            q = (h - lst[6]) / (lst[7])
                            return saturated(p=p, quality=q)
                        elif s is not None:
                            lst = list(saturated(p=p).values())
                            q = (s - lst[9]) / (lst[10] - lst[9])
                            return saturated(p=p, quality=q)

                    elif p == SatWat.index.get_level_values(1)[-1]:
                        return f'At {SatWat.index.get_level_values(1)[-1]} bar,\ngiving an additional property (v/u/h/s) is redundant.\nOnly the pressure is necessary.'
                    else:
                        return 'Pressure not in saturated range.'
                else:
                    return 'Entering a pressure and 2 other properties (v/u/h/s) is redundant.\nEnter a pressure and one of the properties.'

        elif t is not None:
            if quality is not None:  # t and q
                if 0 <= quality <= 1:
                    if [v, u, h, s].count(None) == 4:
                        return QualityCalculation().pt(t, quality, SatWat.index.get_level_values(0))
                    else:
                        return 'Given a temperature, including quality and another value is redundant.\nFor this, choose one.'
                else:
                    return 'Quality must be between 0 and 1.'

            elif quality is None:
                if [v, u, h, s].count(None) == 4:  # only t
                    if t in SatWat.index.get_level_values(0):
                        return return_row(t, SatWat.index.get_level_values(0))
                    elif SatWat.index.get_level_values(0)[0] < t < SatWat.index.get_level_values(0)[-1]:
                        return InterpolateRow(SatWat.index.get_level_values(0), SatWat.index, t).simple()
                    else:
                        return 'Temperature not in saturated range'

                elif [v, u, h, s].count(None) == 3:  # t and v/u/h/s
                    if SatWat.index.get_level_values(0)[0] <= t < SatWat.index.get_level_values(0)[-1]:
                        if v is not None:
                            lst = list(saturated(t=t).values())
                            q = (v - lst[2]) / (lst[3] - lst[2])
                            return saturated(t=t, quality=q)
                        elif u is not None:
                            lst = list(saturated(t=t).values())
                            q = (u - lst[4]) / (lst[5] - lst[4])
                            return saturated(t=t, quality=q)
                        elif h is not None:
                            lst = list(saturated(t=t).values())
                            q = (h - lst[6]) / (lst[7])
                            return saturated(t=t, quality=q)
                        elif s is not None:
                            lst = list(saturated(t=t).values())
                            q = (s - lst[9]) / (lst[10] - lst[9])
                            return saturated(t=t, quality=q)

                    elif t == SatWat.index.get_level_values(0)[-1]:
                        return f'At {SatWat.index.get_level_values(0)[-1]} bar, giving an additional property (v/u/h/s) is redundant.\nOnly the temperature is necessary.'
                    else:
                        return 'Temperature not in saturated range.'
                else:
                    return 'Entering a temperature and 2 other properties (v/u/h/s) is redundant.\nEnter a temperature and one of the properties.'

    elif [p, t].count(None) == 0:
        return 'In a saturated values table,\npressure and temperature are equivalent values (redundant).\nPlease only use one.'
