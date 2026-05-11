import io
import threading
 
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.style.use('dark_background')
import pygame

from enum import IntEnum
from typing import Optional
from .AbstractStrategy import AbstractStrategy
from algorithms import MWURegretTracker, WeightedMajorityRegretTracker

class TrackedAbstractStrategy(AbstractStrategy):
    def __init__(self, options: IntEnum, regret_tracker: Optional[MWURegretTracker | WeightedMajorityRegretTracker] = None):
        super().__init__(options)
        
        self._regret_tracker = regret_tracker
        
        self.probability_history = []
        self.win_history = []   # 1 is win, 0 is loss/draw
        
        # Graph rendering variables
        self._graph_surface = None
        self._graph_lock = threading.Lock()
        self._graph_is_rendering = False
        self._rerender_after_completion = (False, {}) # tuple: ( True|False, {arguments} )

    # --------------------------------------------------
    # graph creation
    # --------------------------------------------------
    def draw_graph(
        self,
        show_weights: bool = True,
        show_bound: bool = True,
        show_expected: bool = True, 
        show_winrate: bool = True,
        show_ratio: bool = True,
        size: tuple[int, int] = (500, 500),
        limit_timesteps: Optional[int] = None
    ) -> None:
        """
        Starts a background thread to render the MWU state graph if there is not one currently running.
        If there is already one running it will mark the flag "_rerender_after_completion"
        """
        if limit_timesteps and limit_timesteps < 0:
            limit_timesteps = None
        
        if self._graph_is_rendering:
            self._rerender_after_completion = (True, {
                "show_weights": show_weights, 
                "show_bound": show_bound,
                "show_expected": show_expected,
                "show_winrate": show_winrate,
                "show_ratio": show_ratio,
                "size": size,
                "limit_timesteps": limit_timesteps,
            })
            return
        
        self._graph_is_rendering = True
        self._start_thread(
            show_weights=show_weights, 
            show_bound=show_bound, 
            show_expected=show_expected, 
            show_winrate=show_winrate,
            show_ratio=show_ratio,
            size=size,
            limit_timesteps=limit_timesteps
        )
    
    def get_new_graph_surface(self):
        """
        Returns rendered self._graph_surface and clears it. 
        """
        with self._graph_lock:
            surface = self._graph_surface
            self._graph_surface = None
        return surface
    
    def _start_thread(self, show_weights, show_bound, show_expected, show_winrate, show_ratio, size, limit_timesteps):
        """ Copy the data to plot in its current state for the thread """
        probability_history  = list(self.probability_history)
        expert_names  = [type(e).__name__ for e in self._experts]
        tracker       = self._regret_tracker
 
        t = None
        history_learner = None
        history_expected = None
        history_best = None
        history_bound = None
        if tracker != None:
            t = tracker.t
            history_learner  = tracker.history_learner.copy()
            history_expected = tracker.history_learner_expected.copy()
            history_best     = tracker.history_best.copy()
            history_bound    = tracker.history_bound.copy()
 
        thread = threading.Thread(
            target=self._render_graph_thread,
            args=(
                show_weights, show_bound, show_expected, show_winrate, show_ratio, size, limit_timesteps,
                expert_names,
                t,
                probability_history,
                history_learner,
                history_expected,
                history_best,
                history_bound
            ),
            daemon=True
        )
        thread.start()
 
    def _render_graph_thread(
        self,
        # Flags & Size
        show_weights, show_bound, show_expected, show_winrate, show_ratio, size, limit_timesteps,
        # Data
        expert_names,
        t,
        probability_history,
        history_learner,
        history_expected,
        history_best,
        history_bound,
    ):
        """ Draws the plot on a different thread and stores to a pygame.Surface (self._graph_surface) """
        try:
            if show_weights and len(probability_history) == 0:
                show_weights = False
            
            layout = f"{"A\n" if show_weights else ""}{"C\n" if show_winrate else ""}{"D\n" if show_ratio else ""}B"
            
            dpi = 100
            figsize = (size[0] / dpi, size[1] / dpi) # pixel size to figure size
            fig, axs = plt.subplot_mosaic(layout, figsize=figsize, dpi=dpi)
            
            timeSteps = [i for i in range(t)]
            
            # Calculate winrate history from win history
            winrate_history = (np.cumsum(self.win_history) / np.arange(1, len(self.win_history) + 1)) * 100 if show_winrate else []

            best_no_zeros = np.where(history_best == 0, 1, history_best)    # remove zeros so there cant be a divide by zero
            ratio_learner = history_learner / best_no_zeros
            ratio_expected = history_expected / best_no_zeros
            ratio_bound = history_bound / best_no_zeros
            
            if limit_timesteps and len(timeSteps) > limit_timesteps:
                timeSteps = timeSteps[-limit_timesteps:]
                probability_history = probability_history[-limit_timesteps:]
                history_learner = history_learner[-limit_timesteps:]
                history_expected = history_expected[-limit_timesteps:]
                history_best = history_best[-limit_timesteps:]
                history_bound = history_bound[-limit_timesteps:]
                winrate_history = winrate_history[-limit_timesteps:]
                ratio_learner = ratio_learner[-limit_timesteps:]
                ratio_expected = ratio_expected[-limit_timesteps:]
                ratio_bound = ratio_bound[-limit_timesteps:]
            
            if show_weights:
                # probability_history: list of arrays, where each array contains all the weights for a specific timestep
                ## Example: [array([0.28571429, 0.28571429, 0.14285714, 0.14285714, 0.14285714]), array([0.30769231, 0.30769231, 0.07692308, 0.15384615, 0.15384615])]
                y_data = np.array(probability_history).T

                axs['A'].stackplot(
                    timeSteps,
                    y_data,
                    labels=expert_names
                )
                axs['A'].set_title('Expert probabilities over time')
                axs['A'].set_xlabel('Time')
                if len(timeSteps) > 1:
                    axs['A'].set_xlim(timeSteps[0], timeSteps[-1])
                axs['A'].set_ylabel('Probability')
                axs['A'].legend(loc="upper left", fontsize="x-small")
                
            if show_winrate:
                if len(winrate_history) > len(timeSteps): # For a race condition where the winrate history is a step ahead of the curren time the graph is processing
                    winrate_history = winrate_history[:len(timeSteps)]
                
                axs['C'].plot(timeSteps, winrate_history, linestyle='-', linewidth=2, label="winrate", color="yellow")
                axs['C'].set_title('Learner winrate over time')
                axs['C'].set_xlabel('Time')
                if len(timeSteps) > 1:
                    axs['C'].set_xlim(timeSteps[0], timeSteps[-1])
                axs['C'].set_ylabel('Winrate (%)')
                axs['C'].set_ylim(0,100)
                axs['C'].legend(loc="upper left", fontsize="x-small")
                axs['C'].grid(True, axis='y')
            
            if show_ratio: 
                axs['D'].plot(timeSteps, ratio_learner, linestyle='-', linewidth=2, label="learner")
                if show_expected:
                    axs['D'].plot(timeSteps, ratio_expected, linestyle='-', linewidth=2, label="expected")
                if show_bound:
                    axs['D'].plot(timeSteps, ratio_bound, linestyle='--', linewidth=2, label="bound")
                axs['D'].set_title('Loss ratios over time')
                axs['D'].set_xlabel('Time')
                axs['D'].set_ylabel('Loss ratio')
                axs['D'].legend(loc="upper left", fontsize="x-small")
            
            ## LOSSES GRAPH
            axs['B'].plot(timeSteps, history_learner, linestyle='-', linewidth=2, label="learner")
            if show_expected:
                axs['B'].plot(timeSteps, history_expected, linestyle='-', linewidth=2, label="expected")
            axs['B'].plot(timeSteps, history_best, linestyle=':', linewidth=2, label="best")
            if show_bound:
                axs['B'].plot(timeSteps, history_bound, linestyle='--', linewidth=2, label="bound")
            axs['B'].set_title('Cumulative loss over time')
            axs['B'].set_xlabel('Time')
            if len(timeSteps) > 1:
                axs['B'].set_xlim(timeSteps[0], timeSteps[-1])
            axs['B'].set_ylabel('Cum. loss')
            axs['B'].legend(loc="upper left", fontsize="small")
                
            # Fix layout (overlap)
            fig.tight_layout(pad=1.5)
                            
            # Save figure to memory buffer 
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            plt.close(fig)
 
            buf.seek(0)
            surface = pygame.image.load(buf, "MWU_graph.png")
 
            with self._graph_lock:
                self._graph_surface = surface
 
        except Exception as e:
            print(f"Graph render error: {e}")
 
        finally:
            if self._rerender_after_completion[0] == True:
                args = self._rerender_after_completion[1]
                self._rerender_after_completion = (False, {})
                self._start_thread(**args)
            else:
                self._graph_is_rendering = False
