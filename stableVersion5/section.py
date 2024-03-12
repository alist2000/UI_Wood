BeamSections = ["4x12", "6x12", "S412", "S612", "S712",
                "2-4x12", "2-6x12", "2S412", "2S612", "2S712",
                "4x10", "6x10", "S410", "S610", "S710",
                "2-4x10", "2-6x10", "2S410", "2S610", "2S710"]


class SelectBeam:
    def __init__(self, sections, m_dcr, v_dcr, deflection_dcr):
        self.sections = sections
        self.m_dcr = m_dcr
        self.v_dcr = v_dcr
        self.deflection_dcr = deflection_dcr

    def final_check(self):
        myIndex = self.check_section()
        if myIndex == "next":
            myIndex = self.check_dcr(self.m_dcr)
            if myIndex == "next":
                myIndex = self.check_dcr(self.v_dcr)
                if myIndex == "next":
                    myIndex = self.check_dcr(self.deflection_dcr)
                    if myIndex == "next":
                        return 0
        return myIndex

    def check_section(self):
        item1 = BeamSections.index(self.sections[0])
        item2 = BeamSections.index(self.sections[1])
        if item1 > item2:
            return 0
        elif item2 > item1:
            return 1
        else:
            return "next"

    @staticmethod
    def check_dcr(dcr):
        if dcr[0] > dcr[1]:
            return 0
        elif dcr[1] > dcr[0]:
            return 1
        else:
            return "next"
