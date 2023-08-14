import sys

sys.path.append(r"D:\git\Wood")

import sqlite3
from WOOD_DESIGN.posts import PostDesign
from WOOD_DESIGN.postlink1 import PostLink1


class MainPost:
    def __init__(self, postdata):
        self.postdata=postdata
        self.query=None

        a=PostLink1(postdata)
        a.pointdata()
        sds=1.32
        

        conn2 = sqlite3.connect('..\..\WOOD_DESIGN\posts.db')
        c2 = conn2.cursor()
        c2.execute(" SELECT * FROM Sizes4")
        sizes={}
        row2=c2.fetchall()



        for r in row2[0:12]:
            z=PostDesign(a.height,a.width, r)
            z.add_load(sds,a.RD, a.RL, a.RLr, a.RE)
            z.Fc_star()
            le_to_d=z.height*12/z.info[2]
            fce=0.822*z.info[13]/(le_to_d**2)
            Fcperp=z.Pmax[0]*1000/z.info[8]
            z.C_p(fce)
            z.Fc_prime()
            z.fc_prime()
            z.post_dcr()
                        
            if z.info[2]==z.width-0.5:
                if z.dcr_max<=1 and Fcperp/625<=1:
                    sizes['Size']=z.info[0]
                    sizes['Grade']=z.info[7]
                    sizes['Pa (k)']=z.fcprime_c*z.info[8]/1000
                    sizes["f'c (psi)"]=z.fcprime_c
                    sizes['Cp']=z.Cp_c
                    sizes['P allowable']=z.Fcprime_c*z.info[8]
                    sizes["F'c"]=z.Fcprime_c
                    sizes['DCR']=z.dcr_max
                    sizes['Governing load combo']=z.combo_max            
                    sizes['Fc perp']=Fcperp
                    sizes['Governing load combo sill']=z.maxcombo0
                    sizes['DCR sill plate']=Fcperp/625
                    self.query=[sizes['Size'], sizes['Grade'], sizes['Pa (k)'], sizes["f'c (psi)"], sizes['Cp'], sizes['P allowable'],sizes["F'c"],sizes['DCR'],sizes['Governing load combo'],sizes['Fc perp'],sizes['Governing load combo sill'],sizes['DCR sill plate']]
                    break
                else:
                    continue

            else:
                continue

        print(sizes)
