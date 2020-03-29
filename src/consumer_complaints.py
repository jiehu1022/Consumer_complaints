#!/usr/bin/python3
"""
    author: Jie Hu
    email: tojiehu@gmail.com
    date: 2020-03-30
"""



import sys
import functools

def super_split(line):
  s = []
  pre = 0
  inside_quota = False
  for i in range(0, len(line)):
    if line[i] == ',' and inside_quota == False:
      s.append(line[pre:i])
      pre = i + 1
    if line[i] == '"':
      inside_quota = (not inside_quota)
  s.append(line[pre:])
  return s


"""
  process the complaint and extract the data. 
  the product should be low case
"""
def process_complaint(line):
  s = super_split(line)
  if len(s) != 18:
    return (-1 , -1, -1, -1)
  id = s[-1]
  try:
    product = s[1].strip().lower()
    year = int(s[0].strip().split('-')[0])
    company = s[7].strip().lower()
    return (id, product, year, company)
  except Exception as ex:
    return (-1, -1, -1, -1)

"""
  1.read data form the input file
  2.preprocess the data include dedup
  3.return the product_data
"""
def process_data(f):
  ids = set()
  ids.add(-1)
  product_data = {}
  with open(f) as complaints:
    complaints.readline()
    for line in complaints:
      line = line.strip()
      (id, product, year, company) = process_complaint(line)
      # if we get duplicate complaint
      # we should pass
      if id in ids:
        continue
      ids.add(id)
      if product not in product_data:
        product_data[product] = {}
      if year not in  product_data[product]:
        product_data[product][year] = [0, 0, set()]
      # total number complains from the year and product
      product_data[product][year][0] =  product_data[product][year][0] + 1
      # total number of companies receiving at least one complaint for that product and year
      product_data[product][year][2].add(company)
      product_data[product][year][1] = len(product_data[product][year][2])
  return product_data

def complain_cmp(a, b):
  pa = a[0]
  pb = b[0]
  if pa[0] == '"':
    pa = pa[1:-1]
  if pb[0] == '"':
    pb = pb[1:-1]

  if pa > pb:
    return 1
  elif pa < pb:
    return -1
  if a[1] > b[1]:
    return 1
  else:
    return -1


def caculate_and_sort(product_data):
  data = []
  for item in product_data.items():
    product = item[0]
    for year_item in item[1].items():
      year = year_item[0]
      total_complains = year_item[1][0]
      total_company = year_item[1][1]
      percentage = round(total_company / total_complains * 100)
      data.append([product, year, total_complains, total_company, percentage])
  data = sorted(data, key=functools.cmp_to_key(complain_cmp))
  return data


def output(data, output_file_name):
  try:
    # open file and with write
    with open(output_file_name, "w") as output_file:
        # write the first line
        output_file.writelines("product,year,total_complaints,total_company_receive_more,highest percentage\n")
        for item in data:
            product = item[0]
            year = item[1]
            total_complaints = item[2]
            total_company_receive_more =item[3]
            highest_percentage = item[4]
            output_file.writelines(
                "%s,%d,%d,%d,%d\n" % (product, year, total_complaints,total_company_receive_more, highest_percentage)
            )
  except IOError as e:
    print("Output Results:I/O error({0}): {1}".format(e.errno, e.strerror))
  except Exception as ex:
    print(ex)
  pass

if __name__ == "__main__":
  if len(sys.argv) < 3:
    exit(1)
  complaints_file = sys.argv[1]
  output_file_name = sys.argv[2]
  data = process_data(complaints_file)
  sorted_data = caculate_and_sort(data)
  output(sorted_data, output_file_name)