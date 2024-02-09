
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
from scipy.stats import kurtosis
from scipy.stats import skew
from scipy import stats




class Features(object):

    def extract(self, flows, selected_flows):
        """Extract the features for each flow in flows, along with KS test features against selected_flows."""
        result = dict()
        for flow_id, flow in flows.items():
             result[flow_id] = self.extract_single_with_ks(flow, selected_flows)
        return result

    def extract_single(self, flow):
        """Extract the features for a single flow."""
        incoming = np.array([f for f in flow if f < 0])
        outgoing = np.array([f for f in flow if f >= 0])
        combined = np.array(flow)

        result = np.concatenate([
            self.features(incoming),
            self.features(outgoing),
            self.features(combined)
        ])

        result[np.isnan(result)] = 0
        return result


    def extract_single_with_ks(self, flow, selected_flows):
        """Extract the features for a single flow, including KS test features for each flow type."""
        incoming = np.array([f for f in flow if f < 0])
        outgoing = np.array([f for f in flow if f >= 0])
        combined = np.array(flow)

        # Extract basic features for each flow type
        basic_features_incoming = self.features(incoming)
        basic_features_outgoing = self.features(outgoing)
        basic_features_combined = self.features(combined)

        # Append KS features for each flow type
        ks_features_incoming = self.append_ks_features(incoming, selected_flows)
        ks_features_outgoing = self.append_ks_features(outgoing, selected_flows)
        ks_features_combined = self.append_ks_features(combined, selected_flows)

        # Combine all features
        result = np.concatenate([
            basic_features_incoming, ks_features_incoming,
            basic_features_outgoing, ks_features_outgoing,
            basic_features_combined, ks_features_combined,
        ])

        result[np.isnan(result)] = 0
        return result


    def features(self, array):
        """Compute statistical features for an array."""
        df = pd.Series(array)
        return [
            df.min(),
            df.max(),
            df.mean(),
            df.mad(),
            df.std(),
            df.var(),
            df.skew(),
            df.kurtosis(),
            np.percentile(array, 10) if array.shape[0] else 0,
            np.percentile(array, 20) if array.shape[0] else 0,
            np.percentile(array, 30) if array.shape[0] else 0,
            np.percentile(array, 40) if array.shape[0] else 0,
            np.percentile(array, 50) if array.shape[0] else 0,
            np.percentile(array, 60) if array.shape[0] else 0,
            np.percentile(array, 70) if array.shape[0] else 0,
            np.percentile(array, 80) if array.shape[0] else 0,
            np.percentile(array, 90) if array.shape[0] else 0,
            df.shape[0]
        ]


    def append_ks_features(self, flow, selected_flows):
        """Append KS test features based on selected_flows."""
        ks_features = []
        for key in selected_flows:
            ks_distances = []
            for selected_flow in selected_flows[key]:
                # Check if either flow is empty before performing KS test
                if len(flow) > 0 and len(selected_flow) > 0:
                    ks_statistic = ks_2samp(flow, selected_flow).statistic
                    ks_distances.append(ks_statistic)
                else:
                    # Handle the case where one or both flows are empty
                    ks_distances.append(0)  # append 0 as a default value

            mean_ks_distance = np.mean(ks_distances) if ks_distances else 0
            std_ks_distance = np.std(ks_distances) if ks_distances else 0
            ks_features.extend([mean_ks_distance,std_ks_distance])
        return ks_features


