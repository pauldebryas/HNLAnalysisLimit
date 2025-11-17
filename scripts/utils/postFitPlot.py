#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
import os
import argparse
from array import array
import ROOT
import yaml 

ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)

# -------------------------------------------------------
# Utility helpers
# -------------------------------------------------------
def list_keys(dirobj):
    return [k.GetName() for k in dirobj.GetListOfKeys()] if dirobj else []

def get_obj(dirobj, name):
    if not dirobj:
        return None
    obj = dirobj.Get(name)
    if obj and not obj.IsZombie():
        return obj
    return None

def get_bin_edges_from_hist(h):
    nb = h.GetNbinsX()
    edges = [h.GetXaxis().GetBinLowEdge(1)]
    for i in range(1, nb + 1):
        edges.append(h.GetXaxis().GetBinUpEdge(i))
    return edges

def remake_hist_same_bins(h, ref_edges, newname):
    if not h or not h.InheritsFrom("TH1"):
        return None
    nb = h.GetNbinsX()
    if len(ref_edges) != nb + 1:
        raise RuntimeError("Ref edges size ({0}) != nbins+1 ({1})".format(len(ref_edges), nb + 1))
    arr = array('d', ref_edges)
    hnew = ROOT.TH1D(newname, h.GetTitle(), nb, arr)
    hnew.Sumw2()
    for i in range(1, nb + 1):
        hnew.SetBinContent(i, h.GetBinContent(i))
        hnew.SetBinError(i,   h.GetBinError(i))
    hnew.GetXaxis().SetTitle(h.GetXaxis().GetTitle())
    hnew.GetYaxis().SetTitle(h.GetYaxis().GetTitle())
    return hnew

def build_ref_path(base, tag, channel, dv, period, mass):
    filename = "HNL_{0}_{1}_M{2}.input.root".format(channel, period, mass)
    return os.path.join(base, tag, channel, dv, "common", filename)

def maybe_load_ref_hist(args, ref_dir_name):
    ref_file_path = args.ref_file
    if not ref_file_path:
        ref_file_path = build_ref_path(args.ref_base, args.tag, args.channel, args.dv, args.period, args.mass)

    if not os.path.isfile(ref_file_path):
        print("WARNING: reference file not found:", ref_file_path)
        return None, None

    rf = ROOT.TFile.Open(ref_file_path)
    if not rf or rf.IsZombie():
        print("WARNING: could not open reference file:", ref_file_path)
        return None, None

    rdir = rf.Get(ref_dir_name) 
    if not rdir:
        print("WARNING: directory '{0}' not found. Top-level: {1}".format(
            ref_dir_name, ", ".join(list_keys(rf))))
        rf.Close()
        return None, None

    rh = get_obj(rdir, args.ref_hist)
    if not rh or not rh.InheritsFrom("TH1"):
        print("WARNING: histogram '{0}' not found (or not TH1) in '{1}'. Found: {2}".format(
            args.ref_hist, ref_dir_name, ", ".join(list_keys(rdir))))
        rf.Close()
        return None, None

    return rf, rh

def graph_to_hist_by_index(g, ref_edges, name="data_hist_from_graph"):
    """Convert TGraph/TGraphAsymmErrors -> TH1 by bin index (no redistribution)."""
    from array import array
    if not g or not (g.InheritsFrom("TGraph") or g.InheritsFrom("TGraphErrors") or g.InheritsFrom("TGraphAsymmErrors")):
        return None, False
    nb = len(ref_edges) - 1
    arr_edges = array('d', ref_edges)
    h = ROOT.TH1D(name, "", nb, arr_edges)
    h.Sumw2()
    npts = g.GetN()
    ok = (npts == nb)
    n = min(npts, nb)
    xbuf = array('d', [0.0]); ybuf = array('d', [0.0])
    for i in range(n):
        g.GetPoint(i, xbuf, ybuf)
        yi = float(ybuf[0])
        e = 0.0
        if g.InheritsFrom("TGraphAsymmErrors"):
            try:
                eyl = float(g.GetErrorYlow(i)); eyh = float(g.GetErrorYhigh(i))
            except Exception:
                try:
                    eyl = float(g.GetEYlow()[i]); eyh = float(g.GetEYhigh()[i])
                except Exception:
                    eyl, eyh = 0.0, 0.0
            e = max(eyl, eyh)
        else:
            try:
                e = float(g.GetErrorY(i))
            except Exception:
                e = 0.0
        h.SetBinContent(i+1, yi)
        h.SetBinError(i+1, e)
    return h, ok

def load_yaml_labels(channel, dv):
    """Load x/y titles from histogram YAML file."""
    yaml_path = "/afs/cern.ch/user/p/pdebryas/HNL_analysis/Analysis/PlotKit/common/config/all/histograms/histograms_{0}.yaml".format(channel)
    if not os.path.isfile(yaml_path):
        print("WARNING: YAML config not found:", yaml_path)
        return None, None
    with open(yaml_path, 'r') as f:
        try:
            conf = yaml.safe_load(f)
        except Exception as e:
            print("WARNING: YAML parse failed:", e)
            return None, None
    if dv not in conf:
        print("WARNING: Key '{}' not found in {}".format(dv, yaml_path))
        return None, None
    entry = conf[dv]
    return entry.get('x_title', None), entry.get('y_title', None)

def load_yaml_lumi(period):
    yaml_path = lumi_file = "/afs/cern.ch/user/p/pdebryas/HNL_analysis/Analysis/PlotKit/common/config/{0}/{1}_lumi.yaml".format(period,period)
    if not os.path.isfile(yaml_path):
        print("WARNING: YAML config not found:", yaml_path)
        return None, None
    with open(yaml_path, 'r') as f:
        try:
            conf = yaml.safe_load(f)
        except Exception as e:
            print("WARNING: YAML parse failed:", e)
            return None, None
    if "lumi_text" not in conf:
        print("WARNING: Key '{}' not found in {}".format("lumi_text", yaml_path))
        return None, None
    entry = conf["lumi_text"]
    return entry.get('text', None)

# -------------------------------------------------------
# Main
# -------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Post-fit plotter with YAML axis labels (Python2.7)")
    parser.add_argument("-i", "--input", required=True, help="fitDiagnostics*.root file")
    parser.add_argument("--fit", choices=["prefit", "postfit-b", "postfit-s"], default="postfit-b", help="Which shapes to plot")
    parser.add_argument("--tag", required=True, help="tag used in config")
    parser.add_argument("--dv", required=True, help="DV key used in YAML (e.g. mT_total_tmm)")
    parser.add_argument("--period", required=True, help="Period")
    parser.add_argument("-c", "--channel", required=True, help="Channel used in ref filename")
    parser.add_argument("--mass", required=True, help="Mass number")
    # optional args
    parser.add_argument("--xTitle", default="", help="Override X axis title")
    parser.add_argument("--yTitle", default="Events", help="Override Y axis title")
    parser.add_argument("--ref-file", default=None, help="Direct path to ref ROOT file")
    parser.add_argument("--ref-base", default="HNLAnalysis/results/datacards", help="Base dir for datacards")
    parser.add_argument("--ref-hist", default="data_obs", help="Histogram name for edges")

    args = parser.parse_args()

    # ---- Load YAML titles ----
    yaml_x, yaml_y = load_yaml_labels(args.channel, args.dv)
    if yaml_x and not args.xTitle:
        if args.dv == 'DNNscore':
            args.xTitle = "{0} {1} GeV".format(yaml_x, args.mass)
        else:
            args.xTitle = yaml_x
    if yaml_y and args.yTitle == "Events":
        args.yTitle = yaml_y

    # ---- ROOT I/O ----
    fit_dir_map = {"prefit": "shapes_prefit", "postfit-b": "shapes_fit_b", "postfit-s": "shapes_fit_s"}
    fit_dir = fit_dir_map[args.fit]
    fin = ROOT.TFile.Open(args.input)
    if not fin or fin.IsZombie():
        raise RuntimeError("Could not open {}".format(args.input))
    base = fin.Get(fit_dir)
    chan = base.Get("HNL_{0}_0_{1}".format(args.channel, args.period))
    h_bkg = get_obj(chan, "total_background")  # keep for uncertainty band & scaling
    h_sig = get_obj(chan, "total_signal")
    if not h_sig:
        h_sig = h_bkg.Clone("sig_empty")
        h_sig.Reset("ICES")

    # New: fetch the two background components for stacking
    h_fake = get_obj(chan, "FakeBackground")
    h_true = get_obj(chan, "TrueLepton")

    # Safety: if one component is missing, replace it with an empty clone so the stack logic works
    if (not h_fake) and h_bkg:
        h_fake = h_bkg.Clone("FakeBackground_empty"); h_fake.Reset("ICES")
    if (not h_true) and h_bkg:
        h_true = h_bkg.Clone("TrueLepton_empty"); h_true.Reset("ICES")

    g_dat = get_obj(chan, "data") or get_obj(chan, "data_obs")

    # Reference edges
    ref_file, ref_hist = maybe_load_ref_hist(args, "HNL_{0}_0_{1}".format(args.channel, args.period))
    data_hist = None
    if ref_hist:
        ref_edges = get_bin_edges_from_hist(ref_hist)
        if len(ref_edges) == h_bkg.GetNbinsX() + 1:
            h_bkg = remake_hist_same_bins(h_bkg, ref_edges, "total_background_refedges")
            h_sig = remake_hist_same_bins(h_sig, ref_edges, "total_signal_refedges")
            if h_fake: h_fake = remake_hist_same_bins(h_fake, ref_edges, "FakeBackground_refedges")
            if h_true: h_true = remake_hist_same_bins(h_true, ref_edges, "TrueLepton_refedges")
            if g_dat and g_dat.InheritsFrom("TGraph"):
                data_hist, ok = graph_to_hist_by_index(g_dat, ref_edges)
                if not ok:
                    print("WARNING: data points != nbins; drawing original graph.")
        else:
            print("WARNING: mismatch between nbins fitDiagnostics ({}) and reference ({})"
                  .format(h_bkg.GetNbinsX(), len(ref_edges)-1))

    # --- Auto-rescale signal to be visually comparable ---
    if h_sig and h_sig.Integral() > 0:
        bkg_max = h_bkg.GetMaximum()
        sig_max = h_sig.GetMaximum()
        if sig_max > 0:
            scale = bkg_max / sig_max * 0.8  # 0.8 keeps it slightly lower than background
            h_sig.Scale(scale)
            print("Scaled signal by factor {:.3f} to match background height".format(scale))

    # ---- Plot ----
    ROOT.gStyle.SetOptStat(0)

    c = ROOT.TCanvas("c","c",800,700)
    pad_top = ROOT.TPad("pad_top","pad_top",0.0,0.30,1.0,1.0)  # top 70%
    pad_bot = ROOT.TPad("pad_bot","pad_bot",0.0,0.00,1.0,0.30)  # bottom 30%

    # Top pad styling
    pad_top.SetTicks(1,1)
    pad_top.SetLeftMargin(0.12)
    pad_top.SetRightMargin(0.04)
    pad_top.SetBottomMargin(0.04)

    # Bottom pad styling
    pad_bot.SetTicks(1,1)
    pad_bot.SetLeftMargin(0.12)
    pad_bot.SetRightMargin(0.04)
    pad_bot.SetTopMargin(0.02)
    pad_bot.SetBottomMargin(0.35)
    pad_bot.SetGridy(True)

    pad_top.Draw()
    pad_bot.Draw()
    pad_top.cd()
    pad_top.SetLogy()

    # Colors/fills for stack components (tweak as you like)
    # Use distinct fills so grayscale prints are readable.
    if h_fake:
        h_fake.SetFillColor(ROOT.TColor.GetColor(250,150, 80))  # orange
        h_fake.SetLineColor(ROOT.kBlack)
        h_fake.SetLineWidth(1)
    if h_true:
        h_true.SetFillColor(ROOT.TColor.GetColor(100,192,232))  # light blue
        h_true.SetLineColor(ROOT.kBlack)
        h_true.SetLineWidth(1)

    # Build the stack from TrueLepton (bottom) + FakeBackground (top)
    st_bkg = ROOT.THStack("st_bkg", "")
    # Order bottom-to-top:
    if h_fake: st_bkg.Add(h_fake, "HIST")
    if h_true: st_bkg.Add(h_true, "HIST")

    # Draw the stack; axes are created on first Draw
    st_bkg.Draw("HIST")

    # Axes: set only Y on top; X title goes to ratio
    if args.yTitle: st_bkg.GetYaxis().SetTitle(args.yTitle)
    st_bkg.GetXaxis().SetTitle("")  # hide on top

    h_err = h_bkg.Clone("err")
    h_err.SetFillStyle(3354)
    h_err.SetFillColor(ROOT.kGray+2)
    h_err.SetLineWidth(0)
    h_err.Draw("E2 SAME")

    h_sig.SetLineColor(ROOT.kRed)
    h_sig.SetLineWidth(2)
    h_sig.Draw("HIST SAME")

    if data_hist:
        data_hist.SetMarkerStyle(20)
        data_hist.Draw("PE SAME")
        data_obj = data_hist
    elif g_dat:
        g_dat.SetMarkerStyle(20)
        g_dat.Draw("P SAME")
        data_obj = g_dat
    else:
        data_obj = None
    
    ymax_stack = st_bkg.GetMaximum()
    ymax_sig   = h_sig.GetMaximum() if h_sig and h_sig.Integral() > 0 else 0.0
    ymax = max(ymax_stack, ymax_sig)
    st_bkg.SetMaximum(10 * (ymax if ymax > 0 else 1.0))

    leg = ROOT.TLegend(0.60, 0.68, 0.95, 0.90)
    # Order: data, signal, components, uncertainty
    if data_obj: leg.AddEntry(data_obj, "Data", "PE")
    if h_sig and h_sig.Integral() > 0: leg.AddEntry(h_sig, "HNL #rightarrow 3l m_{HNL} = "+args.mass+" GeV (arb. scale)    ", "L")
    if h_fake and h_fake.Integral() > 0: leg.AddEntry(h_fake, "Fake background", "F")
    if h_true and h_true.Integral() > 0: leg.AddEntry(h_true, "True lepton", "F")
    leg.AddEntry(h_err, "Bkg. unc.", "F")
    leg.Draw()

    lab = ROOT.TLatex()
    lab.SetNDC(True)
    lab.SetTextSize(0.04)
    lumi = load_yaml_lumi(args.period)
    lab.DrawLatex(0.14,0.93,"CMS data/simulation (Private work)  -  {0}  -  {1}  -  {2}".format(args.fit,args.channel, lumi))

    # -------------------------
    # Ratio pad: Obs / Bkg
    # -------------------------
    pad_bot.cd()

    # Try to ensure we have a binned data histogram aligned to h_bkg
    ratio_data_hist = None
    if data_hist:
        ratio_data_hist = data_hist.Clone("h_ratio_data")
        ratio_data_hist.SetDirectory(0)
    elif g_dat and h_bkg:
        # Try to coerce graph -> hist by index using current binning
        try:
            ref_edges_local = get_bin_edges_from_hist(h_bkg)
            _tmp, _ok = graph_to_hist_by_index(g_dat, ref_edges_local, "h_ratio_data_from_graph")
            if _tmp and _ok:
                ratio_data_hist = _tmp
        except Exception as _e:
            pass

    # Background ratio band = 1 +/- (sigma_bkg / bkg)
    h_ratio_unc = None
    if h_bkg:
        h_ratio_unc = h_bkg.Clone("h_ratio_unc")
        h_ratio_unc.SetDirectory(0)
        nb = h_bkg.GetNbinsX()
        for i in range(1, nb+1):
            b = h_bkg.GetBinContent(i)
            e = h_bkg.GetBinError(i)
            if b > 0.0:
                h_ratio_unc.SetBinContent(i, 1.0)
                h_ratio_unc.SetBinError(i, e / b)
            else:
                h_ratio_unc.SetBinContent(i, 0.0)
                h_ratio_unc.SetBinError(i, 0.0)

        # Style for the uncertainty band
        h_ratio_unc.SetFillStyle(3354)
        h_ratio_unc.SetFillColor(ROOT.kGray+2)
        h_ratio_unc.SetLineWidth(0)

    # Data ratio points = data / bkg, err = data_err / bkg
    h_ratio_data = None
    if ratio_data_hist and h_bkg:
        h_ratio_data = ratio_data_hist.Clone("h_ratio_data_points")
        h_ratio_data.SetDirectory(0)
        nb = h_bkg.GetNbinsX()
        for i in range(1, nb+1):
            d  = ratio_data_hist.GetBinContent(i)
            de = ratio_data_hist.GetBinError(i)
            b  = h_bkg.GetBinContent(i)
            if b > 0.0:
                h_ratio_data.SetBinContent(i, d / b)
                h_ratio_data.SetBinError(i,   de / b)
            else:
                h_ratio_data.SetBinContent(i, 0.0)
                h_ratio_data.SetBinError(i,   0.0)
        h_ratio_data.SetMarkerStyle(20)
        h_ratio_data.SetMarkerSize(0.9)
        h_ratio_data.SetLineColor(ROOT.kBlack)

    # Choose a frame: draw the band first to create axes
    frame_drawn = False
    if h_ratio_unc:
        h_ratio_unc.GetYaxis().SetTitle("Obs./Bkg")
        if args.xTitle: h_ratio_unc.GetXaxis().SetTitle(args.xTitle)

        # Axis cosmetics for split pads
        h_ratio_unc.GetYaxis().SetNdivisions(505)
        h_ratio_unc.GetYaxis().SetTitleSize(0.10)
        h_ratio_unc.GetYaxis().SetLabelSize(0.09)
        h_ratio_unc.GetYaxis().SetTitleOffset(0.5)
        h_ratio_unc.GetXaxis().SetTitleSize(0.12)
        h_ratio_unc.GetXaxis().SetLabelSize(0.10)

        # --- Dynamic ratio range using ROOT GetMaximum/GetMinimum ---
        ratio_max = h_ratio_unc.GetMaximum()
        ratio_min = h_ratio_unc.GetMinimum()

        # If data exist, include them too
        if h_ratio_data:
            ratio_max = max(ratio_max, h_ratio_data.GetMaximum())
            ratio_min = min(ratio_min, h_ratio_data.GetMinimum())

        # Add a small margin so error bars are visible
        margin = 1.0 * (ratio_max - ratio_min if ratio_max > ratio_min else 0.2)
        h_ratio_unc.SetMinimum(ratio_min - margin)
        h_ratio_unc.SetMaximum(ratio_max + margin)
        h_ratio_unc.SetTitle("")
        h_ratio_unc.Draw("E2")

        frame_drawn = True

    # Horizontal line at ratio = 1
    xmin = h_bkg.GetXaxis().GetXmin()
    xmax = h_bkg.GetXaxis().GetXmax()
    line1 = ROOT.TLine(xmin, 1.0, xmax, 1.0)
    line1.SetLineStyle(2)
    line1.SetLineWidth(2)
    line1.SetLineColor(ROOT.kBlack)
    if frame_drawn:
        line1.Draw("SAME")

    # Draw data points on top
    if h_ratio_data:
        drawopt_ratio = "PE SAME"  # include errors if present
        h_ratio_data.SetTitle("")
        h_ratio_data.Draw(drawopt_ratio)

    # Return to top pad for any further annotations if needed
    pad_top.cd()

    c.SaveAs("plot_{0}_{1}.pdf".format(args.channel, args.mass))

if __name__ == "__main__":
    main()
