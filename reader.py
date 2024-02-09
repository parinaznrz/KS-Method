
from scapy.all import *
import numpy as np
import ipaddress

class Reader(object):
    def __init__(self, verbose=False):
        """Reader object for reading packets from .pcap files.

        Parameters
        ----------
        verbose : boolean, default=False
            If True, print which files are being read.
        """
        self.verbose = verbose

    def read(self, infile):
        """Read TCP and UDP packets from input file.

        Parameters
        ----------
        infile : string
            pcap file from which to read packets.

        Returns
        -------
        result : list
            List of packets extracted from pcap file.
            Each packet is represented as a list of:
             - timestamp
             - IP source (in byte representation)
             - IP destination (in byte representation)
             - protocol source port
             - protocol destination port
             - packet length.
        """
        # Initialize the packets list
        self.packets = []

        # If verbose, print loading file
        if self.verbose:
            print("Loading {}...".format(infile))

        # Process both TCP and UDP packets in infile
        sniff(prn=self.extract, lfilter=lambda x: TCP in x or UDP in x, offline=infile)

        # Convert to numpy array
        self.packets = np.array(self.packets)
        # In case of packets, sort on timestamp
        if self.packets.shape[0]:
            # Sort based on timestamp
            self.packets = self.packets[self.packets[:, 0].argsort()]

        # Return extracted packets
        return self.packets

    def extract(self, packet):
        """Extract relevant fields from given packet and adds it to global
           self.packets variable.

        Parameters
        ----------
        packet : scapy.IP
            Scapy IP packet extracted by sniff function.
        """
        # elif
        # Check if the packet is TCP or UDP
        if TCP in packet:
            protocol = packet["TCP"]
        elif UDP in packet:
            protocol = packet["UDP"]
        else:
            # If neither TCP nor UDP, skip the packet
            return
        # Check if the packet is TCP or UDP
        if TCP in packet:
            prot = 1
        elif UDP in packet:
            prot = 0
        else:
            # If neither TCP nor UDP, skip the packet
            return

        # Extract relevant content from packet
        data = [float(packet.time),
                int(ipaddress.ip_address(packet["IP"].src)),
                int(ipaddress.ip_address(packet["IP"].dst)),
                protocol.sport,
                protocol.dport,
                prot,
                packet["IP"].len]

        # Add packet to buffer
        self.packets.append(data)
