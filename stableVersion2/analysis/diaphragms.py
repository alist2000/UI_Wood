import sys

sys.path.append(r"D:\git\Wood")
from WOOD_DESIGN.elfp import Elfp

class Diaphragms(Elfp):
    ''' 
    For each story
    '''
    def __init__(self, wings, lines, midline_area, load_map, story_num, ratio):
        self.lines=lines
        self.lines_flat=[]
        self.midline_area=midline_area
        self.load_map=load_map
        self.weight_line=[]
        self.weight_line_flat=[]
        self.weight_line=[]
        self.story_num=story_num
        self.wings=wings
        self.ratio=ratio

        self.force_per_line()
        
        
    def force_per_line(self):
        
        
        weight_0=[[] for i in self.lines]
        for wi, wng in enumerate(self.midline_area):
            for li, lin in enumerate(wng):
                weight_0[wi].append([])
                for ai, ar in enumerate(lin):
                    wt=ar*self.load_map[wi][li][ai]
                    weight_0[wi][li].append(wt/1000)

        
        
        weight=[[] for i in self.lines]
        for wgi, wg in enumerate(weight_0):
            for ln in wg:
                weight[wgi].append(sum(ln))
              
        
        weight_line_0=[[] for i in self.lines]
        for wii, wgg in enumerate(weight):
            it=0
            for sm in wgg:
                weight_line_0[wii].append(sm/2+it/2)
                it= sm
            weight_line_0[wii].append(wgg[-1]/2)
         
        # ## Find similar lines in each wing
        sim_lines=list(set.intersection(*[set(list) for list in self.lines]))
        self.lines_flat0=[i for k in self.lines for i in k]
        self.weight_line_flat0=[i for k in weight_line_0 for i in k]
        

        ## Find indexes of similar lines 
        ind=[]
        for kk in sim_lines:
            ind.append([i for i,x in enumerate(self.lines_flat0) if x==kk])


        # Add weights of similar lines and delete duplicates    
        for ik in ind:
            self.weight_line_flat0[ik[0]]=sum([self.weight_line_flat0[i] for i in ik])
                    
        for ik2 in ind:
            for ik3 in ik2[1:]:           
                self.weight_line_flat0[ik3]=0
                self.lines_flat0[ik3]=0 

        self.weight_line_flat=[i for i in self.weight_line_flat0 if i!=0 ] 
        self.lines_flat=[i for i in self.lines_flat0 if i!=0 ]         

        self.weight_line=[i*self.ratio for i in self.weight_line_flat]
  
            

                
        