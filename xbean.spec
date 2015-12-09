%{?_javapackages_macros:%_javapackages_macros}
# Conditionals to help breaking eclipse <-> xbean dependency cycle
# when bootstrapping for new architectures
%if 0%{?fedora}
%bcond_without equinox
%bcond_without spring
%endif

Name:           xbean
Version:        3.17
BuildArch:      noarch

Release:        2.1
Summary:        Java plugin based web server

License:        ASL 2.0
URL:            http://geronimo.apache.org/xbean/

Source0:        http://repo2.maven.org/maven2/org/apache/%{name}/%{name}/%{version}/%{name}-%{version}-source-release.zip

# Fix dependency on xbean-asm4-shaded to original objectweb-asm
Patch0:         %{name}-asm4-unshade.patch
# Compatibility with Eclipse Luna (rhbz#1087461)
Patch1:         %{name}-luna.patch

BuildRequires:  java-devel
BuildRequires:  apache-commons-beanutils
BuildRequires:  apache-commons-logging
BuildRequires:  objectweb-asm
BuildRequires:  ant
BuildRequires:  qdox
BuildRequires:  slf4j
BuildRequires:  maven-local
BuildRequires:  maven-plugin-bundle
BuildRequires:  maven-antrun-plugin
BuildRequires:  maven-compiler-plugin
BuildRequires:  maven-dependency-plugin
BuildRequires:  maven-install-plugin
BuildRequires:  maven-javadoc-plugin
BuildRequires:  maven-resources-plugin
BuildRequires:  maven-surefire-plugin
BuildRequires:  maven-site-plugin
BuildRequires:  maven-shade-plugin
%if %{with equinox}
BuildRequires:  eclipse-equinox-osgi
%else
BuildRequires:  felix-framework
%endif
%if %{with spring}
BuildRequires:  apache-commons-jexl
BuildRequires:  aries-blueprint
# test deps BuildRequires:  cglib
BuildRequires:  felix-osgi-compendium
BuildRequires:  felix-osgi-core
BuildRequires:  geronimo-annotation
BuildRequires:  pax-logging

BuildRequires:  maven-archiver
BuildRequires:  maven-plugin-plugin
BuildRequires:  maven-project
BuildRequires:  plexus-archiver
BuildRequires:  plexus-utils
BuildRequires:  springframework
BuildRequires:  springframework-beans
BuildRequires:  springframework-context
BuildRequires:  springframework-web
%endif

%description
The goal of XBean project is to create a plugin based server
analogous to Eclipse being a plugin based IDE. XBean will be able to
discover, download and install server plugins from an Internet based
repository. In addition, we include support for multiple IoC systems,
support for running with no IoC system, JMX without JMX code,
lifecycle and class loader management, and a rock solid Spring
integration.

%if %{with spring}
# For now blueprint module fails to compile. Disable it.
%if 0
%package        blueprint
Summary:        Schema-driven namespace handler for Apache Aries Blueprint

%description    blueprint
This package provides %{summary}.
%endif

%package        classloader
Summary:        A flexibie multi-parent classloader

%description    classloader
This package provides %{summary}.

%package        spring
Summary:        Schema-driven namespace handler for spring contexts
Requires:       %{name} = %{version}-%{release}

%description    spring
This package provides %{summary}.

%package        -n maven-%{name}-plugin
Summary:        XBean plugin for Apache Maven

%description    -n maven-%{name}-plugin
This package provides %{summary}.
%endif

%package        javadoc
Summary:        API documentation for %{name}

%description    javadoc
This package provides %{summary}.

%prep
%setup -q
# build failing on this due to doxia-sitetools problems
rm src/site/site.xml

%patch0
#patch1

%pom_remove_parent
%pom_remove_dep mx4j:mx4j
%pom_remove_dep :xbean-asm5-shaded xbean-reflect

# These aren't needed for now
%pom_disable_module xbean-asm5-shaded
%pom_disable_module xbean-finder-shaded
%pom_disable_module xbean-telnet

# Prevent modules depending on springframework from building.
%if %{without spring}
   %pom_remove_dep org.springframework:
   #%%pom_disable_module xbean-blueprint
   %pom_disable_module xbean-classloader
   %pom_disable_module xbean-spring
   %pom_disable_module maven-xbean-plugin
%else
   %mvn_package :xbean-classloader classloader
   %mvn_package :xbean-spring spring
   %mvn_package :maven-xbean-plugin maven-xbean-plugin
%endif
# blueprint FTBFS, disable for now
%pom_disable_module xbean-blueprint


# Replace generic OSGi dependencies with either Equinox or Felix
%pom_remove_dep :org.osgi.core xbean-bundleutils
%pom_remove_dep org.eclipse:osgi xbean-bundleutils
%if %{with equinox}
  %pom_add_dep org.eclipse.osgi:org.eclipse.osgi xbean-bundleutils
%else
  rm -rf xbean-bundleutils/src/main/java/org/apache/xbean/osgi/bundle/util/equinox/
  %pom_add_dep org.apache.felix:org.apache.felix.framework xbean-bundleutils
%endif

# maven-xbean-plugin invocation makes no sense as there are no namespaces
%pom_remove_plugin :maven-xbean-plugin xbean-classloader

# As auditing tool RAT is useful for upstream only.
%pom_remove_plugin :apache-rat-plugin


# disable copy of internal aries-blueprint
sed -i "s|<Private-Package>|<!--Private-Package>|" xbean-blueprint/pom.xml
sed -i "s|</Private-Package>|</Private-Package-->|" xbean-blueprint/pom.xml

# Fix ant groupId
find -name pom.xml -exec sed -i "s|<groupId>ant</groupId>|<groupId>org.apache.ant</groupId>|" {} \;
# Fix cglib artifactId
find -name pom.xml -exec sed -i "s|<artifactId>cglib-nodep</artifactId>|<artifactId>cglib</artifactId>|" {} \;

%build
%mvn_build -f

%install
%mvn_install

%files -f .mfiles
%doc LICENSE NOTICE
%dir %{_javadir}/%{name}

%if %{with spring}
%if 0
%files blueprint -f .mfiles-blueprint
%doc LICENSE NOTICE %{name}-blueprint/target/restaurant.xsd*
%endif

%files classloader -f .mfiles-classloader
%doc LICENSE NOTICE

%files spring -f .mfiles-spring
%doc LICENSE NOTICE

%files -n maven-%{name}-plugin -f .mfiles-maven-%{name}-plugin
%doc LICENSE NOTICE
%endif

%files javadoc -f .mfiles-javadoc
%doc LICENSE NOTICE

%changelog
* Thu Aug 08 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.13-4
- Update to latest packaging guidelines

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.13-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Apr 29 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.13-2
- Remove unneeded BR: maven-idea-plugin

* Fri Mar 15 2013 Michal Srb <msrb@redhat.com> - 3.13-1
- Update to upstream version 3.13

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.12-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 3.12-5
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Mon Dec 17 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.12-4
- Enable xbean-spring, resolves rhbz#887496
- Disable xbean-blueprint due to FTBFS

* Mon Oct 22 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.12-3
- Replace eclipse-rcp requires with eclipse-equinox-osgi
- Reenable Equinox

* Tue Oct 16 2012 gil cattaneo <puntogil@libero.it> - 3.12-2
- Enable xbean-blueprint and xbean-classloader modules

* Wed Oct 10 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.12-1
- Update to upstream version 3.12

* Wed Oct 10 2012 Krzysztof Daniel <kdaniel@redhat.com> 3.11.1-8
- Revert previous changes.

* Wed Oct 10 2012 Krzysztof Daniel <kdaniel@redhat.com> 3.11.1-7
- Disable parts dependent on Eclipse (for bootstraping purpose).

* Wed Oct 10 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.11.1-6
- Implement equinox and spring conditionals

* Mon Sep  3 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.11.1-5
- Fix eclipse requires

* Mon Aug 27 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.11.1-4
- Fix felix-framework enabling patch

* Mon Aug  6 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.11.1-3
- Enable xbean-spring
- Enable maven-xbean-plugin
- Remove RPM bug workaround

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.11.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jul 13 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.11.1-1
- Update to the upstream version 3.11.1
- Force use of Equinox instead of Felix
- Convert patch to POM macros

* Thu May  3 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.8-5
- Remove mx4j from deps (javax.management provided by JDK 1.5+)

* Tue Apr 24 2012 Alexander Kurtakov <akurtako@redhat.com> 3.8-4
- BR felix-framework instead of felix-osgi-core.

* Tue Apr 24 2012 Alexander Kurtakov <akurtako@redhat.com> 3.8-3
- Do not build equinox specific parts for RHEL.

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Dec  6 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.8-1
- Update to latest upstream version
- Build with maven 3
- Packaging & guidelines fixes

* Sat May 28 2011 Marek Goldmann <mgoldman@redhat.com> - 3.7-7
- Added xbean-finder and xbean-bundleutils submodules

* Fri Mar  4 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.7-6
- Add comment for removing javadoc
- Fix maven 3 build

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.7-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Dec  6 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.7-4
- Fix pom filename (Resolves rhbz#655827)
- Add depmap for main pom file
- Fixes according to new guidelines (versionless jars, javadocs)

* Fri Jul 30 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.7-3
- Use javadoc:aggregate to generate javadocs

* Fri Jul  9 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.7-2
- Add license to javadoc subpackage

* Mon Jun 21 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.7-1
- First release
