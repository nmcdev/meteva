from meteva.perspact.verify.verificate import verificate,creat_middle_result,verificate_with_middle_result
import time
from meteva.perspact.verify.para_example import para


start = time.time()
verificate(para)
end = time.time()
print(end - start)