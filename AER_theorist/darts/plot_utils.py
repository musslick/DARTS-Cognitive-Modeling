import AER_config as aer_config
import AER_theorist.darts.darts_config as darts_config
import matplotlib.pyplot as plt
from matplotlib import pyplot
import matplotlib
import pylab
import seaborn as sns
from matplotlib.gridspec import GridSpec
from mpl_toolkits import mplot3d
import imageio
import time
import numpy as np
import os
import pandas

def generate_darts_summary_figures(figure_names,
                                   titles,
                                   filters,
                                   title_suffix,
                                   study_name,
                                   y_name,
                                   y_label,
                                   y_sem_name,
                                   x1_name,
                                   x1_label,
                                   x2_name,
                                   x2_label,
                                   x_limit,
                                   y_limit,
                                   best_model_name,
                                   figure_size,
                                   y_reference=None,
                                   y_reference_label=None,
                                   arch_samp_filter=None,
                                   ):

    for idx, (figure_name, title, theorist_filter) in enumerate(zip(figure_names, titles, filters)):

        print('##########################: ' + figure_name)
        title = title + title_suffix
        if idx > 0:  # after legend
            show_legend = False
            figure_dimensions = figure_size
        else:
            show_legend = True
            figure_dimensions = (6, 6)
        if idx > 1:  # after original darts
            y_label = ' ' #' '

        plot_darts_summary(study_name=study_name,
                           title=title,
                           y_name=y_name,
                           y_label=y_label,
                           y_sem_name=y_sem_name,
                           x1_name=x1_name,
                           x1_label=x1_label,
                           x2_name=x2_name,
                           x2_label=x2_label,
                           metric='mean_min',
                           x_limit=x_limit,
                           y_limit=y_limit,
                           best_model_name=best_model_name,
                           theorist_filter=theorist_filter,
                           arch_samp_filter = arch_samp_filter,
                           figure_name=figure_name,
                           figure_dimensions=figure_dimensions,
                           legend_loc=aer_config.legend_loc,
                           legend_font_size=aer_config.legend_font_size,
                           axis_font_size=aer_config.axis_font_size,
                           title_font_size=aer_config.title_font_size,
                           show_legend=show_legend,
                           y_reference=y_reference,
                           y_reference_label=y_reference_label,
                           save=True)


def plot_darts_summary(study_name, y_name, x1_name,
                       x2_name=None,
                       y_label=None,
                       x1_label=None,
                       x2_label=None,
                       y_sem_name=None,
                       metric='min',
                       y_reference=None,
                       y_reference_label=None,
                       figure_dimensions=None,
                       title='',
                       legend_loc=0,
                       legend_font_size=8,
                       axis_font_size=10,
                       title_font_size=10,
                       show_legend=True,
                       y_limit=None,
                       x_limit=None,
                       theorist_filter=None,
                       arch_samp_filter=None,
                       best_model_name=None,
                       save=False,
                       figure_name='figure'):

    palette = 'PuBu'

    if figure_dimensions is None:
        figure_dimensions = (4, 3)

    if y_label is None:
        y_label = y_name

    if x1_label is None:
        x1_label = x1_name

    if x2_label is None:
        x2_label = x2_name

    if y_reference_label is None:
        y_reference_label = 'Data Generating Model'

    # determine directory for study results and figures
    results_path = aer_config.studies_folder \
                        + study_name + "/" \
                        + aer_config.models_folder \
                        + aer_config.models_results_folder

    figures_path = aer_config.studies_folder \
                   + study_name + "/" \
                   + aer_config.models_folder \
                   + aer_config.models_results_figures_folder

    # read in all csv files
    files = list()
    for file in os.listdir(results_path):
        if file.endswith(".csv"):
            if 'model_' not in file:
                continue

            if theorist_filter is not None:
                if theorist_filter not in file:
                    continue
            files.append(os.path.join(results_path, file))

    print("Found " + str(len(files)) + " files.")

    # generate a plot dictionary
    plot_dict = dict()
    plot_dict[darts_config.csv_arch_file_name] = list()
    plot_dict[y_name] = list()
    plot_dict[x1_name] = list()
    if x2_name is not None:
        plot_dict[x2_name] = list()
    if y_sem_name is not None:
        plot_dict[y_sem_name] = list()

    # load csv files into a common dictionary
    for file in files:
        data = pandas.read_csv(file, header=0)

        valid_data = list()

        # filter for arch samp
        if arch_samp_filter is not None:
            for idx, arch_file_name in enumerate(data[darts_config.csv_arch_file_name]):
                arch_samp = int(float(arch_file_name.split("_sample", 1)[1].split("_", 1)[0]))
                if arch_samp == arch_samp_filter:
                    valid_data.append(idx)
        else:
            for idx in range(len(data[darts_config.csv_arch_file_name])):
                valid_data.append(idx)

        plot_dict[darts_config.csv_arch_file_name].extend(data[darts_config.csv_arch_file_name][valid_data])
        if y_name in data.keys():
            plot_dict[y_name].extend(data[y_name][valid_data])
        else:
            raise Exception('Could not find key "' + y_name + '" in the data file: ' + str(file))
        if x1_name in data.keys():
            plot_dict[x1_name].extend(data[x1_name][valid_data])
        else:
            raise Exception('Could not find key "' + x1_name + '" in the data file: ' + str(file))
        if x2_name is not None:
            if x2_name in data.keys():
                plot_dict[x2_name].extend(data[x2_name][valid_data])
            else:
                raise Exception('Could not find key "' + x2_name + '" in the data file: ' + str(file))
        if y_sem_name is not None:
            # extract seed number from model file name

            if y_sem_name in data.keys():
                plot_dict[y_sem_name].extend(data[y_sem_name])
            elif y_sem_name == 'seed':
                y_sem_list = list()
                for file_name in data[darts_config.csv_arch_file_name][valid_data]:
                    y_sem_list.append(int(float(file_name.split("_s_", 1)[1].split("_sample", 1)[0])))
                plot_dict[y_sem_name].extend(y_sem_list)

            else:

                raise Exception('Could not find key "' + y_sem_name + '" in the data file: ' + str(file))


    model_name_list = plot_dict[darts_config.csv_arch_file_name]
    x1_data = np.asarray(plot_dict[x1_name])
    y_data = np.asarray(plot_dict[y_name])
    if x2_name is None: # determine for each value of x1 the corresponding y
        x1_data = np.asarray(plot_dict[x1_name])
        x1_unique = np.sort(np.unique(x1_data))

        y_plot = np.empty(x1_unique.shape)
        y_plot[:] = np.nan
        y_sem_plot = np.empty(x1_unique.shape)
        y_sem_plot[:] = np.nan
        y2_plot = np.empty(x1_unique.shape)
        y2_plot[:] = np.nan
        x1_plot = np.empty(x1_unique.shape)
        x1_plot[:] = np.nan
        for idx_unique, x1_unique_val in enumerate(x1_unique):
            y_match = list()
            model_name_match = list()
            for idx_data, x_data_val in enumerate(x1_data):
                if x1_unique_val == x_data_val:
                    y_match.append(y_data[idx_data])
                    model_name_match.append(model_name_list[idx_data])
            x1_plot[idx_unique] = x1_unique_val

            if metric is 'min':
                y_plot[idx_unique] = np.min(y_match)
                idx_target = np.argmin(y_match)
                legend_label_spec = ' (min)'
            elif metric is 'max':
                y_plot[idx_unique] = np.max(y_match)
                idx_target = np.argmax(y_match)
                legend_label_spec = ' (max)'
            elif metric is 'mean':
                y_plot[idx_unique] = np.mean(y_match)
                idx_target = 0
                legend_label_spec = ' (avg)'
            elif metric is 'mean_min':
                y_plot[idx_unique] = np.mean(y_match)
                y2_plot[idx_unique] = np.min(y_match)
                idx_target = np.argmin(y_match)
                legend_label_spec = ' (avg)'
                legend_label2_spec = ' (min)'
            elif metric is 'mean_max':
                y_plot[idx_unique] = np.mean(y_match)
                y2_plot[idx_unique] = np.max(y_match)
                idx_target = np.argmax(y_match)
                legend_label_spec = ' (avg)'
                legend_label2_spec = ' (max)'
            else:
                raise Exception('Argument "metric" may either be "min", "max", "mean", "mean_min" or "min_max".')

            # compute standard error along given dimension
            if y_sem_name is not None:
                y_sem_data = np.asarray(plot_dict[y_sem_name])
                y_sem_unique = np.sort(np.unique(y_sem_data))
                y_sem = np.empty(y_sem_unique.shape)
                # first average y over all other variables
                for idx_y_sem_unique, y_sem_unique_val in enumerate(y_sem_unique):
                    y_sem_match = list()
                    for idx_y_sem, (y_sem_data_val, x1_data_val, y_data_val) in enumerate(zip(y_sem_data, x1_data, y_data)):
                        if y_sem_unique_val == y_sem_data_val and x1_unique_val == x1_data_val:
                            y_sem_match.append(y_data_val)
                    y_sem[idx_y_sem_unique] = np.mean(y_sem_match)
                # now compute sem
                y_sem_plot[idx_unique] = np.nanstd(y_sem) / np.sqrt(len(y_sem))


            print(x1_label + " = " + str(x1_unique_val) + " (" + str(y_plot[idx_unique]) + "): " + model_name_match[idx_target])

    else: # determine for each combination of x1 and x2 (unique rows) the lowest y
        x2_data = np.asarray(plot_dict[x2_name])
        x2_unique = np.sort(np.unique(x2_data))

        y_plot = list()
        y_sem_plot = list()
        y2_plot = list()
        x1_plot = list()
        x2_plot = list()
        for idx_x2_unique, x2_unique_val in enumerate(x2_unique):

            # collect all x1 and y values matching the current x2 value
            model_name_x2_match = list()
            y_x2_match=list()
            x1_x2_match = list()
            for idx_x2_data, x2_data_val in enumerate(x2_data):
                if x2_unique_val == x2_data_val:
                    model_name_x2_match.append(model_name_list[idx_x2_data])
                    y_x2_match.append(y_data[idx_x2_data])
                    x1_x2_match.append(x1_data[idx_x2_data])

            # now determine unique x1 values for current x2 value
            x1_unique = np.sort(np.unique(x1_x2_match))
            x1_x2_plot = np.empty(x1_unique.shape)
            x1_x2_plot[:] = np.nan
            y_x2_plot = np.empty(x1_unique.shape)
            y_x2_plot[:] = np.nan
            y_sem_x2_plot = np.empty(x1_unique.shape)
            y_sem_x2_plot[:] = np.nan
            y2_x2_plot = np.empty(x1_unique.shape)
            y2_x2_plot[:] = np.nan
            for idx_x1_unique, x1_unique_val in enumerate(x1_unique):
                y_x2_x1_match = list()
                model_name_x2_x1_match = list()
                for idx_x1_data, x1_data_val in enumerate(x1_x2_match):
                    if x1_unique_val == x1_data_val:
                        model_name_x2_x1_match.append(model_name_x2_match[idx_x1_data])
                        y_x2_x1_match.append(y_x2_match[idx_x1_data])
                x1_x2_plot[idx_x1_unique] = x1_unique_val

                if metric is 'min':
                    y_x2_plot[idx_x1_unique] = np.min(y_x2_x1_match)
                    idx_target = np.argmin(y_x2_x1_match)
                    legend_label_spec = ' (min)'
                elif metric is 'max':
                    y_x2_plot[idx_x1_unique] = np.max(y_x2_x1_match)
                    idx_target = np.argmax(y_x2_x1_match)
                    legend_label_spec = ' (max)'
                elif metric is 'mean':
                    y_x2_plot[idx_x1_unique] = np.mean(y_x2_x1_match)
                    idx_target = 0
                    legend_label_spec = ' (avg)'
                elif metric is 'mean_min':
                    y_x2_plot[idx_x1_unique] = np.mean(y_x2_x1_match)
                    y2_x2_plot[idx_x1_unique] = np.min(y_x2_x1_match)
                    idx_target = np.argmin(y_x2_x1_match)
                    legend_label_spec = ' (avg)'
                    legend_label2_spec = ' (min)'
                elif metric is 'mean_max':
                    y_x2_plot[idx_x1_unique] = np.mean(y_x2_x1_match)
                    y2_x2_plot[idx_x1_unique] = np.max(y_x2_x1_match)
                    idx_target = np.argmax(y_x2_x1_match)
                    legend_label_spec = ' (avg)'
                    legend_label2_spec = ' (max)'
                else:
                    raise Exception('Argument "metric" may either be "min", "max", "mean", "mean_min" or "min_max".')

                # compute standard error along given dimension
                if y_sem_name is not None:
                    y_sem_data = np.asarray(plot_dict[y_sem_name])
                    y_sem_unique = np.sort(np.unique(y_sem_data))
                    y_sem = np.empty(y_sem_unique.shape)
                    # first average y over all other variables
                    for idx_y_sem_unique, y_sem_unique_val in enumerate(y_sem_unique):
                        y_sem_match = list()
                        for idx_y_sem, (y_sem_data_val, x1_data_val, x2_data_val, y_data_val) in enumerate(
                                zip(y_sem_data, x1_data, x2_data, y_data)):
                            if y_sem_unique_val == y_sem_data_val and x1_unique_val == x1_data_val and x2_unique_val == x2_data_val :
                                y_sem_match.append(y_data_val)
                        y_sem[idx_y_sem_unique] = np.nanmean(y_sem_match)
                    # now compute sem
                    y_sem_x2_plot[idx_x1_unique] = np.nanstd(y_sem) / np.sqrt(len(y_sem))

                if metric is 'mean_min' or metric is 'mean_max':
                    best_val_str = str(y2_x2_plot[idx_x1_unique])
                else:
                    best_val_str = str(y_x2_plot[idx_x1_unique])

                print(x1_label + " = " + str(x1_unique_val) + ", " + \
                      x2_label + " = " + str(x2_unique_val) + " (" + \
                    best_val_str + "): " + model_name_x2_x1_match[idx_target])

            y_plot.append(y_x2_plot)
            y2_plot.append(y2_x2_plot)
            y_sem_plot.append(y_sem_x2_plot)
            x1_plot.append(x1_x2_plot)
            x2_plot.append(x2_unique_val)
    # plot
    # plt.axhline

    # determine best model coordinates
    best_model_x1 = None
    best_model_x2 = None
    best_model_y = None
    if best_model_name is not None:
        theorist = best_model_name.split("weights_", 1)[1].split("_v_", 1)[0]
        if theorist_filter is not None:
            if theorist_filter==theorist:
                determine_best_model = True
            else:
                determine_best_model = False
        else:
            determine_best_model = True

        if determine_best_model:
            idx = plot_dict[darts_config.csv_arch_file_name].index(best_model_name)
            best_model_x1 = plot_dict[x1_name][idx]
            best_model_x2 = plot_dict[x2_name][idx]
            best_model_y = plot_dict[y_name][idx]


    fig, ax = pyplot.subplots(figsize=figure_dimensions)

    if x2_name is None:

        data_plot = pandas.DataFrame({x1_label:x1_plot, y_label:y_plot})
        # sns.lineplot(x=x1_label, y=y_label, data=data_plot, linewidth = 2, ax=ax)
        colors = sns.color_palette(palette, 10)
        color = colors[-1]
        full_label = 'Reconstructed Model' + legend_label_spec
        sns.lineplot(x=x1_plot, y=y_plot, marker='o', linewidth=2, ax=ax, label=full_label, color=color)

        # draw error bars
        if y_sem_name is not None:
            ax.errorbar(x=x1_plot, y=y_plot, yerr=y_sem_plot, color=color)

        # draw second y value
        if (metric is 'mean_min' or metric is 'mean_max'):
            full_label = 'Reconstructed Model' + legend_label2_spec
            ax.plot(x1_plot, y2_plot, '*', linewidth=2, label=full_label, color=color)

            if show_legend:
                handles, _ = ax.get_legend_handles_labels()
                ax.legend(handles=handles, loc=legend_loc)
                plt.setp(ax.get_legend().get_texts(), fontsize=legend_font_size)

        # draw selected model
        if best_model_x1 is not None and best_model_y is not None:
            ax.plot(best_model_x1, best_model_y, 'o', fillstyle='none', color='black', markersize=10)

        ax.set_xlabel(x1_label, fontsize=axis_font_size)
        ax.set_ylabel(y_label, fontsize=axis_font_size)
        ax.set_title(title, fontsize=title_font_size)

        if y_limit is not None:
            ax.set_ylim(y_limit)

        if x_limit is not None:
            ax.set_xlim(x_limit)

        # generate legend
        # ax.scatter(x1_plot, y_plot, marker='.', c='r')
        # g = sns.relplot(data=data_plot, x=x1_label, y=y_label, ax=ax)
        # g._legend.remove()
        if y_reference is not None:
            ax.axhline(y_reference, c='black', linestyle='dashed', label=y_reference_label)

            if show_legend:
                # generate legend
                handles, _ = ax.get_legend_handles_labels()
                ax.legend(handles=handles, loc=legend_loc)
                plt.setp(ax.get_legend().get_texts(), fontsize=legend_font_size)
    else:

        # produce data frame:
        # x1_df = list()
        # x2_df = list()
        # y_df = list()
        # for idx_x2, x2 in enumerate(x2_plot):
        #     for idx_x1, x1 in enumerate(x1_plot[idx_x2]):
        #         x1_df.append(x1)
        #         x2_df.append(x2)
        #         y_df.append(y_plot[idx_x2][idx_x1])
        #
        # data_plot = pandas.DataFrame({x1_label: x1_df, x2_label: x2_df, y_label: y_df})
        # data_plot[x2_label] = pandas.Categorical(data_plot[x2_label], ordered=True)
        # sns.lineplot(data=data_plot, x=x1_label, y=y_label, hue=x2_label, linewidth = 2, ax=ax)
        # forcing markers same style:
        # sns.lineplot(x="n_index", y="value", hue="logic", style="logic", markers=["o", "o"], data=df)

        colors= sns.color_palette(palette, len(x2_plot))

        for idx, x2 in enumerate(x2_plot):

            x1_plot_line = x1_plot[idx]
            y_plot_line = y_plot[idx]
            label = x2_label + '$ = ' + str(x2) + "$" + legend_label_spec
            color = colors[idx]

            sns.lineplot(x=x1_plot_line, y=y_plot_line, marker='o', linewidth=2, ax=ax, label=label, color=color, alpha=1)

            # draw error bars
            if y_sem_name is not None:
                y_sem_plot_line = y_sem_plot[idx]
                ax.errorbar(x=x1_plot_line, y=y_plot_line, yerr=y_sem_plot_line, color=color, alpha=1)

        # # draw second y value on top
        # for idx, x2 in enumerate(x2_plot):
        #     x1_plot_line = x1_plot[idx]
        #     color = colors[idx]
        #
        #     if metric is 'mean_min' or metric is 'mean_max':
        #         y2_plot_line = y2_plot[idx]
        #         label = x2_label + '$ = ' + str(x2) + "$" + legend_label2_spec
        #         ax.plot(x1_plot_line, y2_plot_line, '*', linewidth=2, label=label, color=color)


        # draw selected model
        if best_model_x1 is not None and best_model_y is not None:
            ax.plot(best_model_x1, best_model_y, 'o', fillstyle='none', color='black', markersize=10)

            for idx, x2 in enumerate(x2_plot):
                if best_model_x2 == x2:
                    color = colors[idx]
            ax.plot(best_model_x1, best_model_y, '*', linewidth=2, label='Best Model', color=color)

        if y_reference is not None:
            ax.axhline(y_reference, c='black', linestyle='dashed', label=y_reference_label)

        handles, _ = ax.get_legend_handles_labels()
        leg = ax.legend(handles=handles, loc=legend_loc, bbox_to_anchor=(1.05, 1)) # , title='Legend'
        plt.setp(ax.get_legend().get_texts(), fontsize=legend_font_size)

        if not show_legend:
            leg.remove()

        if y_limit is not None:
            ax.set_ylim(y_limit)

        if x_limit is not None:
            ax.set_xlim(x_limit)

    sns.despine(trim=True)
    ax.set_ylabel(y_label, fontsize=axis_font_size)
    ax.set_xlabel(x1_label, fontsize=axis_font_size)
    ax.set_title(title, fontsize=title_font_size)
    plt.show()

    # save plot
    if save:
        if not os.path.exists(figures_path):
            os.mkdir(figures_path)
        fig.savefig(os.path.join(figures_path, figure_name))



def plot_model_graph(study_name, arch_weights_name, model_weights_name, object_of_study, figure_name='graph'):

    import AER_theorist.darts.visualize as viz
    import AER_theorist.darts.utils as utils
    import os

    figures_path = aer_config.studies_folder \
                   + study_name + "/" \
                   + aer_config.models_folder \
                   + aer_config.models_results_figures_folder

    model = load_model(study_name, model_weights_name, arch_weights_name, object_of_study)

    (n_params_total, n_params_base, param_list) = model.countParameters(print_parameters=True)
    genotype = model.genotype()
    filepath = os.path.join(figures_path, figure_name)
    viz.plot(genotype.normal, filepath, fileFormat='png',
                         input_labels=object_of_study.__get_input_labels__(), full_label=True, param_list=param_list,
                         out_dim=object_of_study.__get_output_dim__(), out_fnc=utils.get_output_str(object_of_study.__get_output_type__()), viewFile=True)


# old


def load_model(study_name, model_weights_name, arch_weights_name, object_of_study):

    from AER_theorist.darts.model_search import Network
    import AER_theorist.darts.utils as utils
    import torch
    import os

    num_output = object_of_study.__get_output_dim__()
    num_input = object_of_study.__get_input_dim__()
    k = int(float(arch_weights_name.split("_k_", 1)[1].split("_s_", 1)[0]))

    results_weights_path = aer_config.studies_folder \
                           + study_name + "/" \
                           + aer_config.models_folder \
                           + aer_config.models_results_weights_folder

    model_path = os.path.join(results_weights_path, model_weights_name + ".pt")
    arch_path = os.path.join(results_weights_path, arch_weights_name + ".pt")
    criterion = utils.sigmid_mse
    model = Network(num_output,
                    criterion,
                    steps=k,
                    n_input_states=num_input)
    utils.load(model, model_path)
    alphas_normal = torch.load(arch_path)
    model.fix_architecture(True, new_weights=alphas_normal)

    return model

class DebugWindow:

    def __init__(self, num_epochs, numArchEdges=1, numArchOps=1, ArchOpsLabels=(), fitPlot3D = False, show_arch_weights=True):

        # initialization
        matplotlib.use("TkAgg") # need to add this for PyCharm environment

        plt.ion()

        # SETTINGS
        self.show_arch_weights = show_arch_weights
        self.fontSize = 10

        self.performancePlot_limit = (0, 1)
        self.modelFitPlot_limit = (0, 500)
        self.mismatchPlot_limit = (0, 1)
        self.architectureWeightsPlot_limit = (0.1, 0.2)

        self.numPatternsShown = 100

        # FIGURE
        self.fig = plt.figure()
        self.fig.set_size_inches(13, 7)

        if self.show_arch_weights is False:
            numArchEdges = 0

        # set up grid
        numRows = np.max((1+np.ceil((numArchEdges+1)/4), 2))
        gs = GridSpec(numRows.astype(int), 4, figure=self.fig)

        self.fig.subplots_adjust(left=0.1, bottom=0.1, right=0.90, top=0.9, wspace=0.4, hspace=0.5)
        self.modelGraph = self.fig.add_subplot(gs[1, 0])
        self.performancePlot = self.fig.add_subplot(gs[0, 0])
        self.modelFitPlot = self.fig.add_subplot(gs[0, 1])
        if fitPlot3D:
            self.mismatchPlot = self.fig.add_subplot(gs[0, 2], projection='3d')
        else:
            self.mismatchPlot = self.fig.add_subplot(gs[0, 2])
        self.examplePatternsPlot = self.fig.add_subplot(gs[0, 3])

        self.architecturePlot = []

        for edge in range(numArchEdges):
            row = np.ceil((edge+2)/4).astype(int)
            col = ((edge+1) % 4)
            self.architecturePlot.append(self.fig.add_subplot(gs[row, col]))

        self.colors = ('black', 'red', 'green', 'blue', 'purple', 'orange', 'brown', 'pink', 'grey', 'olive', 'cyan', 'yellow', 'skyblue', 'coral', 'magenta', 'seagreen', 'sandybrown')

        # PERFORMANCE PLOT
        x = 1
        y = 1
        self.train_error, = self.performancePlot.plot(x, y, 'r-')
        self.valid_error, = self.performancePlot.plot(x, y, 'b', linestyle='dashed')

        # set labels
        self.performancePlot.set_xlabel('Epoch', fontsize = self.fontSize)
        self.performancePlot.set_ylabel('Cross-Entropy Loss', fontsize = self.fontSize)
        self.performancePlot.set_title('Performance', fontsize = self.fontSize)
        self.performancePlot.legend((self.train_error, self.valid_error), ('training error', 'validation error'))

        # adjust axes
        self.performancePlot.set_xlim(0, num_epochs)
        self.performancePlot.set_ylim(self.performancePlot_limit[0], self.performancePlot_limit[1])

        # MODEL FIT PLOT
        x = 1
        y = 1
        self.BIC, = self.modelFitPlot.plot(x, y, color='black')
        self.AIC, = self.modelFitPlot.plot(x, y, color='grey')

        # set labels
        self.modelFitPlot.set_xlabel('Epoch', fontsize = self.fontSize)
        self.modelFitPlot.set_ylabel('Information Criterion', fontsize = self.fontSize)
        self.modelFitPlot.set_title('Model Fit', fontsize = self.fontSize)
        self.modelFitPlot.legend((self.BIC, self.AIC), ('BIC', 'AIC'))

        # adjust axes
        self.modelFitPlot.set_xlim(0, num_epochs)
        self.modelFitPlot.set_ylim(self.modelFitPlot_limit[0], self.modelFitPlot_limit[1])

        # RANGE PREDICTION FIT PLOT
        x = 1
        y = 1
        if fitPlot3D:
            x = np.arange(0, 1, 0.1)
            y = np.arange(0, 1, 0.1)
            X, Y = np.meshgrid(x, y)
            Z = X * np.exp(-X - Y)

            self.range_target = self.mismatchPlot.plot_surface(X, Y, Z)
            self.range_prediction = self.mismatchPlot.plot_surface(X, Y, Z)
            self.mismatchPlot.set_zlim(self.mismatchPlot_limit[0], self.mismatchPlot_limit[1])

            # set labels
            self.mismatchPlot.set_xlabel('Stimulus 1', fontsize=self.fontSize)
            self.mismatchPlot.set_ylabel('Stimulus 2', fontsize=self.fontSize)
            self.mismatchPlot.set_zlabel('Outcome Value', fontsize=self.fontSize)

        else:
            self.range_target, = self.mismatchPlot.plot(x, y, color='black')
            self.range_prediction, = self.mismatchPlot.plot(x, y, '--', color='red')

            # set labels
            self.mismatchPlot.set_xlabel('Stimulus Value', fontsize=self.fontSize)
            self.mismatchPlot.set_ylabel('Outcome Value', fontsize=self.fontSize)
            self.mismatchPlot.legend((self.range_target, self.range_prediction), ('target', 'prediction'))

        self.mismatchPlot.set_title('Target vs. Prediction', fontsize=self.fontSize)

        # adjust axes
        self.mismatchPlot.set_xlim(0, 1)
        self.mismatchPlot.set_ylim(0, 1)

        # ARCHITECTURE WEIGHT PLOT
        if self.show_arch_weights:

            self.architectureWeights = []
            for idx, architecturePlot in enumerate(self.architecturePlot):
                plotWeights = []
                x = 1
                y = 1
                for op in range(numArchOps):
                    plotWeight, = architecturePlot.plot(x, y, color=self.colors[op])
                    plotWeights.append(plotWeight)

                # set legend
                if(idx == 0):
                    architecturePlot.legend(plotWeights, ArchOpsLabels, prop={'size': 6})

                # add labels
                architecturePlot.set_ylabel('Weight', fontsize = self.fontSize)
                architecturePlot.set_title('(' + str(idx) + ') Edge Weight', fontsize = self.fontSize)
                if(idx == len(self.architecturePlot) - 1):
                    architecturePlot.set_xlabel('Epoch', fontsize = self.fontSize)

                # adjust axes
                architecturePlot.set_xlim(0, num_epochs)
                architecturePlot.set_ylim(self.architectureWeightsPlot_limit[0], self.architectureWeightsPlot_limit[1])

                self.architectureWeights.append(plotWeights)


        # draw
        plt.draw()


    def update(self, train_error=None, valid_error=None, weights=None, BIC=None, AIC=None, model_graph=None, range_input1=None, range_input2=None, range_target=None, range_prediction=None, target=None, prediction=None):

        # update training error
        if train_error is not None:
            self.train_error.set_xdata(np.linspace(1, len(train_error), len(train_error)))
            self.train_error.set_ydata(train_error)

        # update validation error
        if valid_error is not None:
            self.valid_error.set_xdata(np.linspace(1, len(valid_error), len(valid_error)))
            self.valid_error.set_ydata(valid_error)

        # update BIC
        if BIC is not None:
            self.BIC.set_xdata(np.linspace(1, len(BIC), len(BIC)))
            self.BIC.set_ydata(BIC)

        # update AIC
        if AIC is not None:
            self.AIC.set_xdata(np.linspace(1, len(AIC), len(AIC)))
            self.AIC.set_ydata(AIC)

        # update target vs. prediction plot
        if range_input1 is not None and range_target is not None and range_prediction is not None and range_input2 is None:
            self.range_target.set_xdata(range_input1)
            self.range_target.set_ydata(range_target)
            self.range_prediction.set_xdata(range_input1)
            self.range_prediction.set_ydata(range_prediction)
        elif range_input1 is not None and range_target is not None and range_prediction is not None and range_input2 is not None:

            # update plot
            self.mismatchPlot.cla()
            self.range_target = self.mismatchPlot.plot_surface(range_input1, range_input2, range_target, color = (0, 0, 0, 0.5))
            self.range_prediction = self.mismatchPlot.plot_surface(range_input1, range_input2, range_prediction, color = (1, 0, 0, 0.5))

            # set labels
            self.mismatchPlot.set_xlabel('Stimulus 1', fontsize=self.fontSize)
            self.mismatchPlot.set_ylabel('Stimulus 2', fontsize=self.fontSize)
            self.mismatchPlot.set_zlabel('Outcome Value', fontsize=self.fontSize)
            self.mismatchPlot.set_title('Target vs. Prediction', fontsize=self.fontSize)



        # update example pattern plot
        if target is not None and prediction is not None:

            # select limited number of patterns
            self.numPatternsShown = np.min((self.numPatternsShown, target.shape[0]))
            target = target[0:self.numPatternsShown, :]
            prediction = prediction[0:self.numPatternsShown, :]

            im = np.concatenate((target, prediction), axis=1)
            self.examplePatternsPlot.cla()
            self.examplePatternsPlot.imshow(im, interpolation='nearest', aspect='auto')
            x = np.ones(target.shape[0]) * (target.shape[1]-0.5)
            y = np.linspace(1, target.shape[0], target.shape[0])
            self.examplePatternsPlot.plot(x, y, color='red')

            # set labels
            self.examplePatternsPlot.set_xlabel('Output', fontsize=self.fontSize)
            self.examplePatternsPlot.set_ylabel('Pattern', fontsize=self.fontSize)
            self.examplePatternsPlot.set_title('Target vs. Prediction', fontsize=self.fontSize)

        if self.show_arch_weights:
            # update weights
            if weights is not None:
                for plotIdx, architectureWeights in enumerate(self.architectureWeights):
                    for lineIdx, plotWeight in enumerate(architectureWeights):
                        plotWeight.set_xdata(np.linspace(1, weights.shape[0], weights.shape[0]))
                        plotWeight.set_ydata(weights[:, plotIdx, lineIdx])

        # draw current graph
        if model_graph is not None:
            im = imageio.imread(model_graph)
            self.modelGraph.cla()
            self.modelGraph.imshow(im)
            self.modelGraph.axis('off')

        # re-draw plot
        plt.draw()
        plt.pause(0.02)

