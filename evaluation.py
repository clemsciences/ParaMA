'''
Created on Jun 11, 2018

@author: xh
'''

def get_seg_points(seg):
    seg_points = []
    indx = 0
    for i in range(len(seg) - 1):
        indx += len(seg[i])
        seg_points.append(indx)
    return seg_points

def get_best_seg(seg_test, segs_gold):
    seg_points_test = set(get_seg_points(seg_test))
    best_correct, best_total, min_best_total = 0.0, 0.0, 100.0
    best_gold = None
    min_gold_seg = None
    for gold in segs_gold:
        seg_points_gold = set(get_seg_points(gold))
        gold_size = len(seg_points_gold)
        correct = len(seg_points_gold & seg_points_test)
        if (correct > best_correct) or (correct == best_correct and gold_size < best_total):
            best_correct = correct
            best_total = gold_size
            best_gold = gold
        if gold_size < min_best_total:
            min_best_total = gold_size
            min_gold_seg = gold
    if best_total == 0:
        best_total = min_best_total
        best_gold = min_gold_seg
    return best_gold


def eval_seg_points(seg_gold, seg_test):
    if len(seg_gold) != len(seg_test): return 0.0, 0.0, 0.0
    correct_total, gold_total, pred_total = 0, 0, 0
    for i in range(len(seg_gold)):
        goldsegs = seg_gold[i]
        test = seg_test[i]
        word = ''.join(test)
        seg_points_test = set(get_seg_points(test))
        pred_size = len(seg_points_test)
        best_correct, best_total, min_best_total = 0.0, 0.0, 100.0
        for gold in goldsegs:
            gold_word = ''.join(gold)
            if word != gold_word:
                print('Warning: test word different from gold: %s | %s' % (word, gold_word))
            seg_points_gold = set(get_seg_points(gold))
            gold_size = len(seg_points_gold)
            correct = len(seg_points_gold & seg_points_test)
            if (correct > best_correct) or (correct == best_correct and gold_size < best_total):
                best_correct = correct
                best_total = gold_size
            if gold_size < min_best_total:
                min_best_total = gold_size
        if best_total == 0:
            best_total = min_best_total
        correct_total += best_correct
        gold_total += best_total
        pred_total += pred_size
    if pred_total == 0:
        prec = 0.0
    else:
        prec = correct_total * 1.0 / pred_total
    if gold_total == 0:
        rec = 0.0
    else:
        rec = correct_total * 1.0 / gold_total
    if prec + rec == 0.0:
        f1 = 0.0
    else:
        f1 = 2 * prec * rec / (prec + rec)
    return (prec, rec, f1)

def get_seg_morphemes(seg):
    seg_morphemes = []
    sIndx = 0
    for i in range(len(seg)):
        eIndx = sIndx + len(seg[i])
        seg_morphemes.append((sIndx, eIndx))
        sIndx = eIndx
    return seg_morphemes

def calc_performance(tp, fp, fn):
    prec, rec, f1 = 0.0, 0.0, 0.0
    if tp > 0: 
        prec = tp * 1.0 / (tp + fp)
        rec = tp * 1.0 / (tp + fn)
        f1 = 2 * prec * rec / (prec + rec)
    return prec, rec, f1

def eval_seg_morphemes(seg_gold, seg_test):
    if len(seg_gold) != len(seg_test): return 0.0, 0.0, 0.0
    tp, fp, fn = 0, 0, 0
    for i in range(len(seg_gold)):
        goldsegs = seg_gold[i]
        test = seg_test[i]
        seg_morphemes_test = set(get_seg_morphemes(test))
        _prec_best, _rec_best, f1_best = 0.0, 0.0, -1.0
        tp_best, fp_best, fn_best = 0, 0, 0
        for gold in goldsegs:
            seg_morphemes_gold = set(get_seg_morphemes(gold))
            tp_local = len(seg_morphemes_gold & seg_morphemes_test)
            fp_local = len(seg_morphemes_test - seg_morphemes_gold)
            fn_local = len(seg_morphemes_gold - seg_morphemes_test)
            _prec_local, _rec_local, f1_local = calc_performance(tp_local, fp_local, fn_local)
            if f1_local > f1_best or (f1_local == f1_best and fp_local + fn_local < fp_best + fn_best): 
                tp_best, fp_best, fn_best = tp_local, fp_local, fn_local
                f1_best = f1_local
        tp += tp_best
        fp += fp_best
        fn += fn_best
    return calc_performance(tp, fp, fn)

def eval_last_morphemes(seg_gold, seg_test):
    if len(seg_gold) != len(seg_test): return 0.0, 0.0, 0.0
    tp, fp, fn = 0, 0, 0
    for i in range(len(seg_gold)):
        goldsegs = seg_gold[i]
        test = seg_test[i]
        last_morph_indx = {get_seg_morphemes(test)[-1]}
        _prec_best, _rec_best, f1_best = 0.0, 0.0, -1.0
        tp_best, fp_best, fn_best = 0, 0, 0
        for gold in goldsegs:
            seg_morphemes_gold_indx = {get_seg_morphemes(gold)[-1]}
            tp_local = len(seg_morphemes_gold_indx & last_morph_indx)
            fp_local = len(last_morph_indx - seg_morphemes_gold_indx)
            fn_local = len(seg_morphemes_gold_indx - last_morph_indx)
            _prec_local, _rec_local, f1_local = calc_performance(tp_local, fp_local, fn_local)
            if f1_local > f1_best or (f1_local == f1_best and fp_local + fn_local < fp_best + fn_best): 
                tp_best, fp_best, fn_best = tp_local, fp_local, fn_local
                f1_best = f1_local
        tp += tp_best
        fp += fp_best
        fn += fn_best
    return calc_performance(tp, fp, fn)

def evaluate_seg(gold_segs, test_segs):
    prec1, rec1, f11 = eval_last_morphemes(gold_segs, test_segs)
    prec2, rec2, f12 = eval_seg_morphemes(gold_segs, test_segs)
    prec3, rec3, f13 = eval_seg_points(gold_segs, test_segs)
    print('--Result----------Prec.   Rec.    F1-----------')
    print('Seg Points:      (%.4f, %.4f, %.4f)' % (prec3, rec3, f13))
    print('All Morphemes:   (%.4f, %.4f, %.4f)' % (prec2, rec2, f12))
    print('Last Morpheme:   (%.4f, %.4f, %.4f)' % (prec1, rec1, f11))










