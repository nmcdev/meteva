from nmc_verification.nmc_vf_report.verify.verificate import verificate,creat_middle_result,verificate_with_middle_result
import time
from nmc_verification.nmc_vf_report.verify.para_example import para


start = time.time()
verificate(para)
end = time.time()
print(end - start)