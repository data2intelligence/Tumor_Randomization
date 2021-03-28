#!/usr/bin/env python

import os, sys, pandas, numpy, random
from datetime import datetime
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# randomize each time to get different result, if the user doesn't like the previous one
random.seed(datetime.now())

nrand = 1000
font_size = 30
figure_width = 7
current_path = os.getcwd()

plt.rcParams.update({'font.size': font_size})


def boxplot_one(handle, arr, i, col, flag_dot=True):
    """ Generate one box-plot """
    bp = handle.boxplot(arr, widths=0.6, showfliers=False, patch_artist=True, positions=[i])
    
    for median in bp['medians']: median.set(color=col, linewidth=5)
    
    for box in bp['boxes']:
        box.set_facecolor((0,0,0,0))
        #box.set_alpha(alpha)
    
    if flag_dot:
        x = numpy.random.normal(i, 0.1, size=arr.shape[0])
        handle.plot(x, arr, color=col, marker='o', linestyle='none', markersize=5)



def main():
    f = sys.argv[1]
    output = '.'.join(f.split('.')[:-1])
    
    data_map = {}
    
    # load in excel data and do sanity check
    for title in ['Group', 'Size']:
        data = pandas.read_excel(os.path.join(current_path, f), sheet_name=title, index_col=0)
        
        try:
            data = pandas.read_excel(os.path.join(current_path, f), sheet_name=title, index_col=0)
        except:
            sys.stderr.write('Cannot find the %s information\n' % title)
            sys.exit(1)
    
        assert data.index.value_counts().max() == 1    
        data_map[title] = data
    
    # make sure always more mice than the group sum
    size_group = data_map['Group']['Size']
    assert size_group.sum() <= data_map['Size'].shape[0]
    
    # tumor size by area
    for title in ['Short', 'Long']:
        assert title in data_map['Size'].columns
    
    tumor_size = data_map['Size']['Short'] * data_map['Size']['Long']
    tumor_size.name = 'Size'
    
    merge = []
    lst_cache = []
    
    for inx in range(nrand):
        # randomize without changing index
        tumor_size = tumor_size.sample(frac=1)
        
        pos = 0
        
        lst = []
        
        for title, N in size_group.items():
            lst.append(tumor_size.iloc[pos: (pos+N)])
            pos += N
        
        # get minimum p-values
        N = len(lst)
        p_min = 1
        
        # p-value from the maximum difference
        for i in range(N):
            for j in range(i):
                p = stats.ranksums(lst[i], lst[j])[1]
                p_min = min(p_min, p)
        
        # maximum variance
        sd_max = max([v.std() for v in lst])
        
        merge.append(pandas.Series([p_min, sd_max], index=['p_min', 'sd_max'], name=inx))
        lst_cache.append(lst)
    
    result = pandas.concat(merge, axis=1, join='inner').transpose()
    
    # make sure p-value is not significant by any means
    result_rank = result.loc[result['p_min'] > 0.1].rank().astype(int)
    
    # get p_min as big as possible, but sd_max as small as possible
    result_rank = result_rank['p_min'] - result_rank['sd_max']
    result_rank.sort_values(ascending=False, inplace=True)
    
    # diagnostic plots
    pivot = result_rank.index[0]
    
    pdf = PdfPages(output + '.pdf')
    
    fig = plt.figure(figsize=(figure_width, figure_width), frameon=False)
    
    plt.plot(result['p_min'], result['sd_max'], 'o')
    plt.xlabel('pvalue min')
    plt.ylabel('std max')
    
    plt.plot(result.loc[pivot, 'p_min'], result.loc[pivot, 'sd_max'], color='red', marker='+', markersize=20)
    plt.tick_params(pad=10)
    
    pdf.savefig(fig, bbox_inches='tight', transparent=True)
    plt.close(fig)
    
    # box-plots of each group
    lst = lst_cache[pivot]
    
    fig = plt.figure(figsize=(figure_width, figure_width), frameon=False)
    for i, arr in enumerate(lst):
        boxplot_one(plt, arr, i, 'dodgerblue')
    
    plt.xticks(range(len(lst)), size_group.index, rotation=45)
    plt.ylabel('tumor size')
    
    pdf.savefig(fig, bbox_inches='tight', transparent=True)
    plt.close(fig)
    
    pdf.close()
    
    fout = pandas.ExcelWriter(output + '.group.xlsx')
    for i, group in enumerate(lst):
        group.to_excel(fout, size_group.index[i])
    fout.save()

if __name__ == '__main__': main()
