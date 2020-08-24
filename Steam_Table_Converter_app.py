from tkinter import *
from Steam_Table_Converter_Backend import *


class Window:
    def __init__(self, w):
        self.w = w
        self.w.wm_title('Steam Table Calculator')

        l1 = Label(w, text='Temperature')
        l1.grid(row=1, column=1)
        l2 = Label(w, text='Pressure')
        l2.grid(row=2, column=1)
        l3 = Label(w, text='Enthalpy')
        l3.grid(row=3, column=1)
        l4 = Label(w, text='Entropy')
        l4.grid(row=4, column=1)
        l5 = Label(w, text='Internal Energy')
        l5.grid(row=5, column=1)
        l6 = Label(w, text='Specific Volume')
        l6.grid(row=6, column=1)
        l7 = Label(w, text='Quality')
        l7.grid(row=7, column=1)

        # blanks
        lb0 = Label(w, text=' ')
        lb0.grid(row=0, column=0)
        lb1 = Label(w, text=' ')
        lb1.grid(row=0, column=4)
        lb2 = Label(w, text=' ')
        lb2.grid(row=8, column=0)
        lb3 = Label(w, text=' ')
        lb3.grid(row=16, column=0)

        self.temp_text = StringVar(w)
        self.et = Entry(w, textvariable=self.temp_text)
        self.et.grid(row=1, column=2)
        self.pres_text = StringVar(w)
        self.ep = Entry(w, textvariable=self.pres_text)
        self.ep.grid(row=2, column=2)
        self.enthalpy_text = StringVar(w)
        self.eea = Entry(w, textvariable=self.enthalpy_text)
        self.eea.grid(row=3, column=2)
        self.entropy_text = StringVar(w)
        self.eeo = Entry(w, textvariable=self.entropy_text)
        self.eeo.grid(row=4, column=2)
        self.internal_nrg_text = StringVar(w)
        self.eie = Entry(w, textvariable=self.internal_nrg_text)
        self.eie.grid(row=5, column=2)
        self.spec_vol_text = StringVar(w)
        self.esv = Entry(w, textvariable=self.spec_vol_text)
        self.esv.grid(row=6, column=2)
        self.quality_text = StringVar(w)
        self.eq = Entry(w, textvariable=self.quality_text)
        self.eq.grid(row=7, column=2)

        self.listbox1 = Listbox(w, height=11, width=50)
        self.listbox1.grid(row=9, column=1, rowspan=7, columnspan=2)

        b1 = Button(w, text='Calculate Superheated', command=self.execute_superheat)
        b1.grid(row=12, column=3)
        b2 = Button(w, text='Calculate Saturated', command=self.execute_saturated)
        b2.grid(row=11, column=3)
        b3 = Button(w, text='Calculate Compressed', command=self.execute_compress)
        b3.grid(row=13, column=3)

        self.temp_drop = StringVar(w)
        temp_choices = {'C', 'K', 'F', 'R'}
        self.temp_drop.set('C')  # set the default option
        temp_menu = OptionMenu(w, self.temp_drop, *temp_choices)
        temp_menu.grid(row=1, column=3)
        self.pres_drop = StringVar(w)
        pres_choices = {'bar', 'kPa', 'Pa', 'atm', 'torr', 'psi-a'}
        self.pres_drop.set('bar')
        pres_menu = OptionMenu(w, self.pres_drop, *pres_choices)
        pres_menu.grid(row=2, column=3)
        self.enthalpy_drop = StringVar(w)
        enthalpy_choices = {'kJ/kg', 'J/kg', 'erg/g', 'Btu/lbm', 'cal/g', 'cal/lbm', 'lbf.ft/lbm'}
        self.enthalpy_drop.set('kJ/kg')
        enthalpy_menu = OptionMenu(w, self.enthalpy_drop, *enthalpy_choices)
        enthalpy_menu.grid(row=3, column=3)
        self.entropy_drop = StringVar(w)
        entropy_choices = {'kJ/kg-K', 'J/kg-K', 'cal/g-C', 'Btu/lb-F'}
        self.entropy_drop.set('kJ/kg-K')
        entropy_menu = OptionMenu(w, self.entropy_drop, *entropy_choices)
        entropy_menu.grid(row=4, column=3)
        self.intEn_drop = StringVar(w)
        int_en_choices = {'kJ/kg', 'J/kg', 'erg/g', 'Btu/lbm', 'cal/g', 'cal/lbm', 'lbf.ft/lbm'}
        self.intEn_drop.set('kJ/kg')
        int_en_menu = OptionMenu(w, self.intEn_drop, *int_en_choices)
        int_en_menu.grid(row=5, column=3)
        self.spec_vol_drop = StringVar(w)
        spec_vol_choices = {'m3/kg', 'cm3/g', 'L/kg', 'ft3/lb', 'ft3/kg'}
        self.spec_vol_drop.set('m3/kg')
        spec_vol_menu = OptionMenu(w, self.spec_vol_drop, *spec_vol_choices)
        spec_vol_menu.grid(row=6, column=3)
        self.quality_drop = StringVar(w)
        quality_choices = {'decimal', '%'}
        self.quality_drop.set('decimal')  # set the default option
        quality_menu = OptionMenu(w, self.quality_drop, *quality_choices)
        quality_menu.grid(row=7, column=3)

    def execute_superheat(self):
        self.flow_superheat_compress(SupWat)

    def execute_compress(self):
        self.flow_superheat_compress(CompWat)

    def execute_saturated(self):
        self.listbox1.delete(0, END)
        lst = []
        for var in [self.pres_text, self.temp_text, self.spec_vol_text, self.internal_nrg_text, self.enthalpy_text,
                    self.entropy_text, self.quality_text]:
            try:
                lst.append(float(var.get()))
            except ValueError:
                lst.append(None)
        lst = self.unit_conversion_input(lst)
        print(f'p={lst[0]}, t={lst[1]}, v={lst[2]}, u={lst[3]}, h={lst[4]}, s={lst[5]}, q={lst[6]}')
        sat_return = saturated(p=lst[0], t=lst[1], v=lst[2], u=lst[3], h=lst[4], s=lst[5], quality=lst[6])
        if type(sat_return) == dict:
            new_sat_return = self.list_dict(sat_return)
            for i, j in new_sat_return.items():
                self.listbox1.insert(END, f'{i}: {j}')
        elif type(sat_return) == str:
            str_lst = sat_return.split('\n')
            for i in str_lst:
                self.listbox1.insert(END, i)

    def flow_superheat_compress(self, df):
        self.listbox1.delete(0, END)
        lst = []
        for var in [self.pres_text, self.temp_text, self.spec_vol_text, self.internal_nrg_text, self.enthalpy_text,
                    self.entropy_text]:
            try:
                lst.append(float(var.get()))
            except ValueError:
                lst.append(None)
        lst = self.unit_conversion_input(lst)
        print(f'p={lst[0]}, t={lst[1]}, v={lst[2]}, u={lst[3]}, h={lst[4]}, s={lst[5]}')
        func_return = NonSat(df).outer_dome(p=lst[0], t=lst[1], v=lst[2], u=lst[3], h=lst[4], s=lst[5])
        if type(func_return) == list:
            pt_dict = {'Pres': lst[0], 'Temp': func_return[0]}
            pt_dict.update(func_return[1])
            new_sup_return = self.list_dict(pt_dict)
            for i, j in new_sup_return.items():
                self.listbox1.insert(END, f'{i}: {j}')
        elif type(func_return) == dict:
            pt_dict = {'Pres': lst[0], 'Temp': lst[1]}
            pt_dict.update(func_return)
            new_sup_return = self.list_dict(pt_dict)
            for i, j in new_sup_return.items():
                self.listbox1.insert(END, f'{i}: {j}')
        elif type(func_return) == str:
            self.listbox1.insert(END, func_return)

    def list_dict(self, d):
        list_dict_keys = list(d.keys())
        list_dict_values = list(d.values())
        list_dict_values = self.unit_conversion_output(list_dict_keys, list_dict_values)
        return dict(zip(list_dict_keys, list_dict_values))

    def unit_conversion_input(self, lst):
        if self.pres_drop.get() != 'bar':
            if self.pres_drop.get() == 'kPa':
                if lst[0] is not None:
                    lst[0] = lst[0] / 100
            elif self.pres_drop.get() == 'Pa':
                if lst[0] is not None:
                    lst[0] = lst[0] / 100000
            elif self.pres_drop.get() == 'atm':
                if lst[0] is not None:
                    lst[0] = lst[0] * 1.01325
            elif self.pres_drop.get() == 'torr':
                if lst[0] is not None:
                    lst[0] = lst[0] / 750.061682704
            elif self.pres_drop.get() == 'psi-a':
                if lst[0] is not None:
                    lst[0] = lst[0] / 14.503773800722
        if self.temp_drop.get() != 'C':
            if self.temp_drop.get() == 'K':
                if lst[1] is not None:
                    lst[1] = lst[1] - 273.15
            elif self.temp_drop.get() == 'F':
                if lst[1] is not None:
                    lst[1] = (lst[1] - 32) * (5/9)
            elif self.temp_drop.get() == 'R':
                if lst[1] is not None:
                    lst[1] = (lst[1] - 491.67) * (5/9)
        if self.spec_vol_drop.get() != 'm3/kg':
            if self.spec_vol_drop.get() == 'cm3/g':
                if lst[2] is not None:
                    lst[2] = lst[2] * 0.001
            elif self.spec_vol_drop.get() == 'L/kg':
                if lst[2] is not None:
                    lst[2] = lst[2] * 0.001
            elif self.spec_vol_drop.get() == 'ft3/lb':
                if lst[2] is not None:
                    lst[2] = lst[2] * 0.06242795996802
            elif self.spec_vol_drop.get() == 'ft3/kg':
                if lst[2] is not None:
                    lst[2] = lst[2] * 0.02831684659319
        if self.intEn_drop.get() != 'kJ/kg':
            if self.intEn_drop.get() == 'J/kg':
                if lst[3] is not None:
                    lst[3] = lst[3] / 1000
            elif self.intEn_drop.get() == 'erg/g':
                if lst[3] is not None:
                    lst[3] = lst[3] * 10000000
            elif self.intEn_drop.get() == 'Btu/lbm':
                if lst[3] is not None:
                    lst[3] = lst[3] * 2.326
            elif self.intEn_drop.get() == 'cal/g':
                if lst[3] is not None:
                    lst[3] = lst[3] * 4.184
            elif self.intEn_drop.get() == 'cal/lbm':
                if lst[3] is not None:
                    lst[3] = lst[3] * 0.009224141049815279
            elif self.intEn_drop.get() == 'lbf.ft/lbm':
                if lst[3] is not None:
                    lst[3] = lst[3] * 0.0029890669199999997
        if self.enthalpy_drop.get() != 'kJ/kg':
            if self.enthalpy_drop.get() == 'J/kg':
                if lst[4] is not None:
                    lst[4] = lst[4] / 1000
            elif self.enthalpy_drop.get() == 'erg/g':
                if lst[4] is not None:
                    lst[4] = lst[4] * 10000000
            elif self.enthalpy_drop.get() == 'Btu/lbm':
                if lst[4] is not None:
                    lst[4] = lst[4] * 2.326
            elif self.enthalpy_drop.get() == 'cal/g':
                if lst[4] is not None:
                    lst[4] = lst[4] * 4.184
            elif self.enthalpy_drop.get() == 'cal/lbm':
                if lst[4] is not None:
                    lst[4] = lst[4] * 0.009224141049815279
            elif self.enthalpy_drop.get() == 'lbf.ft/lbm':
                if lst[4] is not None:
                    lst[4] = lst[4] * 0.0029890669199999997
        if self.entropy_drop.get() != 'kJ/kg-K':
            if self.entropy_drop.get() == 'J/kg-K':
                if lst[5] is not None:
                    lst[5] = lst[5] * 0.001
            elif self.entropy_drop.get() == 'cal/g-C':
                if lst[5] is not None:
                    lst[5] = lst[5] * 4.1868
            elif self.entropy_drop.get() == 'Btu/lb-F':
                if lst[5] is not None:
                    lst[5] = lst[5] * 4.1868
        if self.quality_drop.get() != 'decimal':
            if self.quality_drop.get() == '%':
                if lst[6] is not None:
                    lst[6] = lst[6] / 100
        return lst

    def unit_conversion_output(self, ldk, ldv):
        for i in ldk:
            if i == 'Pres':
                p_pos = ldk.index('Pres')
                if self.pres_drop.get() == 'bar':
                    ldv[p_pos] = f'{ldv[p_pos]} bar'
                if self.pres_drop.get() == 'kPa':
                    ldv[p_pos] = f'{ldv[p_pos] * 100} kPa'
                if self.pres_drop.get() == 'Pa':
                    ldv[p_pos] = f'{ldv[p_pos] * 100000} Pa'
                if self.pres_drop.get() == 'atm':
                    ldv[p_pos] = f'{ldv[p_pos] / 1.01325} atm'
                if self.pres_drop.get() == 'torr':
                    ldv[p_pos] = f'{ldv[p_pos] * 750.061682704} torr'
                if self.pres_drop.get() == 'psi-a':
                    ldv[p_pos] = f'{ldv[p_pos] / 14.503773800722} psi-a'
            if i == 'Temp':
                t_pos = ldk.index('Temp')
                if self.temp_drop.get() == 'C':
                    ldv[t_pos] = f'{ldv[t_pos]} C'
                if self.temp_drop.get() == 'K':
                    ldv[t_pos] = f'{ldv[t_pos] + 273.15} K'
                if self.temp_drop.get() == 'F':
                    ldv[t_pos] = f'{(ldv[t_pos] * 9 / 5) + 32} F'
                if self.temp_drop.get() == 'R':
                    ldv[t_pos] = f'{(ldv[t_pos] * 9 / 5) + 491.67} R'
            if i == 'v':
                v_pos = ldk.index('v')
                self.unit_conv_element_vol(ldv, v_pos)
            if 'vg' in i:
                vg_pos = ldk.index('Sat Vap vg')
                self.unit_conv_element_vol(ldv, vg_pos)
            if 'vf' in i:
                vf_pos = ldk.index('Sat Liq vf')
                self.unit_conv_element_vol(ldv, vf_pos)
            if i == 'u':
                u_pos = ldk.index('u')
                self.unit_conv_element_u_h(self.intEn_drop.get(), ldv, u_pos)
            if 'ug' in i:
                ug_pos = ldk.index('Sat Vap ug')
                self.unit_conv_element_u_h(self.intEn_drop.get(), ldv, ug_pos)
            if 'uf' in i:
                uf_pos = ldk.index('Sat Liq uf')
                self.unit_conv_element_u_h(self.intEn_drop.get(), ldv, uf_pos)
            if i == 'h':
                h_pos = ldk.index('h')
                self.unit_conv_element_u_h(self.enthalpy_drop.get(), ldv, h_pos)
            if i == 'Sat Liq hf':
                hf_pos = ldk.index('Sat Liq hf')
                self.unit_conv_element_u_h(self.enthalpy_drop.get(), ldv, hf_pos)
            if i == 'Sat Vap hg':
                hg_pos = ldk.index('Sat Vap hg')
                self.unit_conv_element_u_h(self.enthalpy_drop.get(), ldv, hg_pos)
            if i == 'Evap hfg':
                hfg_pos = ldk.index('Evap hfg')
                self.unit_conv_element_u_h(self.enthalpy_drop.get(), ldv, hfg_pos)
            if i == 's':
                s_pos = ldk.index('s')
                self.unit_conv_element_s(ldv, s_pos)
            if 'sg' in i:
                sg_pos = ldk.index('Sat Vap sg')
                self.unit_conv_element_s(ldv, sg_pos)
            if 'sf' in i:
                sf_pos = ldk.index('Sat Liq sf')
                self.unit_conv_element_s(ldv, sf_pos)
            if 'quality' in i:
                q_pos = ldk.index('quality')
                if self.quality_drop.get() == '%':
                    ldv[q_pos] = f'{ldv[q_pos] * 100}%'
        return ldv

    def unit_conv_element_vol(self, ldv, pos):
        if self.spec_vol_drop.get() == 'm3/kg':
            ldv[pos] = f'{ldv[pos]} m3/kg'
        if self.spec_vol_drop.get() == 'cm3/g':
            ldv[pos] = f'{ldv[pos] / 0.001} cm3/kg'
        if self.spec_vol_drop.get() == 'L/kg':
            ldv[pos] = f'{ldv[pos] / 0.001} L/kg'
        if self.spec_vol_drop.get() == 'ft3/lb':
            ldv[pos] = f'{ldv[pos] / 0.06242795996802} ft3/lb'
        if self.spec_vol_drop.get() == 'ft3/kg':
            ldv[pos] = f'{ldv[pos] / 0.02831684659319} ft3/kg'

    @staticmethod
    def unit_conv_element_u_h(drop, ldv, pos):
        if drop == 'kJ/kg':
            ldv[pos] = f'{ldv[pos]} kJ/kg'
        elif drop == 'J/kg':
            ldv[pos] = f'{ldv[pos] * 1000} J/kg'
        elif drop == 'erg/g':
            ldv[pos] = f'{ldv[pos] / 10000000} erg/g'
        elif drop == 'Btu/lbm':
            ldv[pos] = f'{ldv[pos] / 2.326} Btu/lbm'
        elif drop == 'cal/g':
            ldv[pos] = f'{ldv[pos] / 4.184} cal/g'
        elif drop == 'cal/lbm':
            ldv[pos] = f'{ldv[pos] / 0.009224141049815279} cal/lbm'
        elif drop == 'lbf.ft/lbm':
            ldv[pos] = f'{ldv[pos] / 0.0029890669199999997} lbf.ft/lbm'

    def unit_conv_element_s(self, ldv, pos):
        if self.entropy_drop.get() == 'kJ/kg-K':
            ldv[pos] = f'{ldv[pos]} kJ/kg-K'
        if self.entropy_drop.get() == 'J/kg-K':
            ldv[pos] = f'{ldv[pos] / 0.001} J/kg-K'
        elif self.entropy_drop.get() == 'cal/g-C':
            ldv[pos] = f'{ldv[pos] / 4.1868} cal/g-C'
        elif self.entropy_drop.get() == 'Btu/lb-F':
            ldv[pos] = f'{ldv[pos] / 4.1868} Btu/lb-F'


window = Tk()
Window(window)
window.mainloop()
